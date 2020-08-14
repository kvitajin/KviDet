from argparse import ArgumentParser
from queue import Queue
from threading import Thread
from time import sleep, time
from datetime import timedelta
from signal import signal, SIGINT
from os import access, path, R_OK

from tqdm import tqdm

import config as config_file
from detector import ObjectDetector
from threads import loader_thread, detector_thread, tracker_thread
from loader import VideoLoader
from tracker import ObjectTracker


def log(msg: str, bar: tqdm = None, cfg = None):
    if cfg is not None and cfg.SILENT:
        return

    if bar is not None and not bar.disable:
        bar.write(msg)
    else:
        print(msg)


def is_readable_file(parser, arg):
    if not path.isfile(arg) or not access(arg, R_OK):
        parser.error(f"${arg} není validní čitelný soubor!")

    return arg


def kvidet(input_video, config):
    to_detect = Queue()
    to_track = Queue()
    to_summarize = Queue()

    video_loader = VideoLoader(config.FRAME_SKIP)
    object_detector = ObjectDetector()
    object_tracker = ObjectTracker()

    video_loader.load(input_video)

    loader_bar = tqdm(desc="loader progress", total=video_loader.get_video_frame_count() // config.FRAME_SKIP,
                      ascii=True, disable=(not config.PROGRESS))
    detector_bar = tqdm(desc="detection progress", total=video_loader.get_video_frame_count() // config.FRAME_SKIP,
                        ascii=True, disable=(not config.PROGRESS))
    tracker_bar = tqdm(desc="tracker progress", total=video_loader.get_video_frame_count() // config.FRAME_SKIP,
                       ascii=True, disable=(not config.PROGRESS))

    loader = Thread(target=loader_thread, args=(video_loader, to_detect, loader_bar), daemon=True)
    detector = Thread(target=detector_thread, args=(object_detector, to_detect, to_track, detector_bar), daemon=True)
    tracker = Thread(target=tracker_thread, args=(object_tracker, to_track, to_summarize, tracker_bar), daemon=True)

    # stop threads
    def stop_detection(sig, fr):
        video_loader.stop = True
        object_detector.stop = True
        object_tracker.stop = True

    signal(SIGINT, stop_detection)

    loader.start()
    log("loader started", loader_bar, config)

    detector.start()
    log("detector started", detector_bar, config)

    tracker.start()
    log("tracker started", tracker_bar, config)

    loader.join()
    detector.join()
    tracker.join()

    loader_bar.close()
    detector_bar.close()
    tracker_bar.close()

    log("all threads finished", cfg=config)

    summarization_task = to_summarize.get()
    detected_vehicles = summarization_task.payload

    log("sorting vehicles by direction", cfg=config)

    sorted_vehicles_by_direction = {}

    if detected_vehicles is None:
        return sorted_vehicles_by_direction

    for vehicle in detected_vehicles.values():
        for direction, bounding_vectors in config.BOUNDING_VECTORS.items():
            if direction not in sorted_vehicles_by_direction:
                sorted_vehicles_by_direction[direction] = []

            if len(vehicle.position_history) < 2:
                continue

            if vehicle.motion_vector.is_between(bounding_vectors[0], bounding_vectors[1]):
                sorted_vehicles_by_direction[direction].append(vehicle)
    return sorted_vehicles_by_direction


if __name__ == "__main__":
    arg_parser = ArgumentParser(description="Detekce projíždějících aut a jejich směrů")

    arg_parser.add_argument("input_path", help="cesta k videosouboru",
                            type=lambda filename: is_readable_file(arg_parser, filename))
    arg_parser.add_argument("--silent", "-s", help="zda vypisovat na standardní výstup průběh detekce",
                            default=config_file.SILENT, action="store_true")
    arg_parser.add_argument("--debug", "-d", help="zda vypisovat ladící údaje na standardní výstup",
                            default=config_file.DEBUG, action="store_true")
    arg_parser.add_argument("--time", "-t", help="zda vypisovat na standardní výstup dobu strávenou detekcí",
                            default=config_file.TIME, action="store_true")
    arg_parser.add_argument("--progress", "-p", help="zda vypisovat živě průběh detekce na standardní výstup",
                            default=config_file.PROGRESS, action="store_true")
    arg_parser.add_argument("--frame-skip", "-n", help="číst poze každý N-tý snímek",
                            default=config_file.FRAME_SKIP, metavar="N", type=int)

    args = arg_parser.parse_args()

    config = config_file
    config.SILENT = args.silent
    config.DEBUG = args.debug
    config.TIME = args.time
    config.PROGRESS = args.progress
    config.FRAME_SKIP = args.frame_skip

    start_time = time()
    result = kvidet(args.input_path, config)
    end_time = time()

    print("-----------------")
    print("Results:")
    for direction in result:
        print(f"direction: {direction} vehicles: {len(result[direction])}")

    if config.TIME:
        elapsed_time=timedelta(seconds=end_time) - timedelta(seconds=start_time)
        hours, remainder = divmod(int(elapsed_time.total_seconds()), 60 * 60)
        minutes, seconds = divmod(remainder, 60)
        print(f"elapsed time: {hours}h {minutes}m {seconds}s")