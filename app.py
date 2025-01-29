import argparse
import json

from scraper.scraper import Worker


def process_file(file_path):
    try:
        with open(file_path, 'r') as file:
            tasks = json.load(file)

            worker = Worker()
            worker.add_tasks(tasks)
            worker.run_tasks()
            data = worker.get_json_scraped_data()
            print(data)

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
    except Exception as e:
        print(f"Error processing file: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='Process a file provided as command line argument'
    )

    parser.add_argument(
        '-f', '--file',
        type=str,
        required=True,
        help='Path to the JSON file to parse'
    )

    args = parser.parse_args()

    process_file(args.file)


if __name__ == '__main__':
    main()
