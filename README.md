# Wikipedia Event Stream Watcher

This project connects to the Wikipedia Event Stream API and tracks revisions happening in real-time across various Wikipedia domains. It generates reports every minute, showing the updated domains and the users who made changes, focusing on edits for the `en.wikipedia.org` domain. The data is displayed in the terminal.

## Features

- **Tracks Wikipedia Revisions**: Listens to real-time Wikipedia revision data.
- **Reports**: 
  - Generates a report every minute with the following details:
    - Number of Wikipedia domains updated and the list of domains with their respective page updates.
    - List of users who made changes to `en.wikipedia.org`, sorted by their edit counts (excluding bot users).
- **Keeps track of edits in the last 5 minutes**: Reports are generated based on a rolling 5-minute window of data.

## Prerequisites

Ensure you have the following installed:

- Python 3.6 or later
- `requests` library (installable via pip)

## Setup Instructions

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/Kumarakash121/Stream_report.git
cd Stream_report
```

### 2. Install Dependencies
Install the required dependencies using pip:
```bash
pip install requests
```
### 3. Run the Script
Run the Python script to start watching the Wikipedia Event Stream:
```bash
python proj.py
```
