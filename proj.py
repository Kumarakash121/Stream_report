import time
import json
import requests
import sys
from collections import deque

event_window = deque()
MAX_WINDOW_SIZE = 5
start_time = time.time()


RETRY_ATTEMPTS = 5
RETRY_DELAY = 5  

def process_event(event_data):
    if event_data.startswith("data: "):
        event_data = event_data[len("data: "):]

    try:
        data = json.loads(event_data)
        event_time = time.time()
        
        domain = data['meta']['domain']
        page_title = data['page_title']
        user = data['performer']['user_text']
        user_edit_count = data['performer'].get('user_edit_count', 0)
        is_bot = data['performer'].get('user_is_bot', False)

        if is_bot:
            return None

        return {
            'domain': domain,
            'page_title': page_title,
            'user': user,
            'user_edit_count': user_edit_count,
            'event_time': event_time
        }
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON. Event data: {event_data}")
        return None
    except KeyError as e:
        print(f"Error: Missing expected key in event data: {e}")
        return None
    except Exception as e:
        print(f"Error processing event: {e}")
        return None

def update_event_window(event_data):
    processed_event = process_event(event_data)
    if processed_event:
        event_window.append(processed_event)

    current_time = time.time()
    while event_window and (current_time - event_window[0]['event_time'] > 300):
        event_window.popleft()

def generate_reports(minute):
    domain_report = {}
    user_report = {}

    for event in event_window:
        domain = event['domain']
        page_title = event['page_title']
        user = event['user']
        user_edit_count = event['user_edit_count']
        
        if domain not in domain_report:
            domain_report[domain] = set()
        domain_report[domain].add(page_title)

        if domain == 'en.wikipedia.org':
            if user not in user_report:
                user_report[user] = 0
            user_report[user] = max(user_report[user], user_edit_count)

    print(f"\nMinute {minute} Report ")

    print("Domain Report:")
    print(f"Total number of Wikipedia Domains Updated: {len(domain_report)}")
    for domain, pages in sorted(domain_report.items(), key=lambda item: len(item[1]), reverse=True):
        print(f"{domain}: {len(pages)} pages updated")
    
    print("\nUsers Report (for en.wikipedia.org):")
    for user, edit_count in sorted(user_report.items(), key=lambda item: item[1], reverse=True):
        print(f"{user}: {edit_count} edits")

def start_stream():
    url = 'https://stream.wikimedia.org/v2/stream/revision-create'
    minute_counter = 1
    last_report_time = time.time()

    attempt = 0
    while attempt < RETRY_ATTEMPTS:
        try:
            print("Attempting to connect to the stream...")
            with requests.get(url, stream=True) as response:
                if response.status_code != 200:
                    print(f"Error: Failed to connect to stream. Status code: {response.status_code}")
                    return
                
                print("Connected to Wikipedia Event Stream.")
                
                data_buffer = ''
                
                for event in response.iter_lines():
                    if event:
                        event_str = event.decode('utf-8').strip()

                        if event_str.startswith(':') or event_str.startswith('event:') or event_str.startswith('id:'):
                            continue

                        update_event_window(event_str)

                        current_time = time.time()
                        
                        if current_time - last_report_time >= 60:
                            generate_reports(minute_counter)
                            minute_counter += 1
                            last_report_time = current_time
                            
                            
                    elapsed_time = int(time.time() - last_report_time)
                    sys.stdout.write(f"\rWaiting for data... {elapsed_time} seconds elapsed")
                    sys.stdout.flush()
                    time.sleep(0.1)  

            
            break
        
        except requests.RequestException as e:
            print(f"Error while connecting to the stream: {e}")
            attempt += 1
            if attempt < RETRY_ATTEMPTS:
                print(f"Retrying in {RETRY_DELAY} seconds... ({attempt}/{RETRY_ATTEMPTS})")
                time.sleep(RETRY_DELAY)  # Wait before retrying
            else:
                print("Max retries reached. Exiting.")
                return

if __name__ == '__main__':
    start_stream()
