from argparse import ArgumentParser
from queue import Queue
from threading import Thread
from time import sleep, time
from datetime import timedelta, datetime
import config as config_file
from threads import loader_thread, detector_thread, tracker_thread


def kvidet(input_video, config):
    to_detect = Queue()
    to_track = Queue()
    to_summarize = Queue()

    loader = Thread(target=loader_thread, args=(input_video, to_detect), daemon=True)
    detector = Thread(target=detector_thread, args=(to_detect, to_track), daemon=True)
    tracker = Thread(target=tracker_thread, args=(to_track, to_summarize), daemon=True)

    loader.start()
    if not config.SILENT:
        print("loader started")

    detector.start()
    if not config.SILENT:
        print("detector started")

    tracker.start()
    if not config.SILENT:
        print("tracker started")

    if config.DEBUG:
        while to_summarize.empty():
            print(f"to_detect: {to_detect.qsize()} to_track: {to_track.qsize()}")
            sleep(2)

    loader.join()
    if not config.SILENT:
        print("loader finished")

    detector.join()
    if not config.SILENT:
        print("detector finished")

    tracker.join()
    if not config.SILENT:
        print("tracker finished")

    summarization_task = to_summarize.get()
    detected_vehicles = summarization_task.payload

    if not config.SILENT:
        print("sorting vehicles by direction")

    sorted_vehicles_by_direction = {}
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

    arg_parser.add_argument("input_path", help="cesta k videosouboru nebo číslo videokamery")
    arg_parser.add_argument("--silent", "-s", help="zda vypisovat na standardní výstup průběh detekce",
                            default=config_file.SILENT, action="store_true")
    arg_parser.add_argument("--debug", "-d", help="zda vypisovat ladící údaje na standardní výstup",
                            default=config_file.DEBUG, action="store_true")
    arg_parser.add_argument("--time", "-t", help="zda vypisovat standardní výstup čas detekce",
                            default=config_file.TIME, action="store_true")

    args = arg_parser.parse_args()

    config = config_file
    config.SILENT = args.silent
    config.DEBUG = args.debug
    config.TIME = args.time
    start_time = time()

    result = kvidet(args.input_path, config) #
    end_time = time()
    print("Results:")
    for direction in result:
        print(f"direction: {direction} vehicles: {len(result[direction])}")
    if config.TIME:
        formated_time=str(timedelta(seconds=end_time)-timedelta(seconds=start_time))
        print("time:", formated_time)