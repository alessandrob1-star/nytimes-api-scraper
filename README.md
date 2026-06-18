# NYTimes Article Search GUI

A small Python project that searches New York Times articles with the official Article Search API.

It includes both a command-line version and a simple desktop GUI built with `tkinter`.

This project was built as a personal Python/API practice project, focused on API integration, environment variable handling, desktop GUI basics, and safe GitHub publishing without exposing private API keys.

## Features

- Search NYTimes articles by keyword.
- Show article title, publication date, source, section, summary, and link.
- Open selected articles in the browser.
- Store the API key locally with a `.env` file.
- Keep private credentials out of Git with `.gitignore`.

## Setup

Install the dependency:

```powershell
python -m pip install -r requirements.txt
```

## NYTimes API Key

Create your API key from the official NYTimes developer portal:

[https://developer.nytimes.com/get-started](https://developer.nytimes.com/get-started)

Follow the official guide:

1. Sign in or create an account.
2. Register a new app from `My Apps`.
3. Enable access to the API product you need, for this project use `Article Search API`.
4. Save the app.
5. Copy your key from the app's `API Keys` section.

Set your API key in the terminal:

```powershell
$env:NYTIMES_API_KEY="your_api_key_here"
```

Alternatively, create a local `.env` file in this folder:

```text
NYTIMES_API_KEY=your_api_key_here
```

Run the script:

```powershell
python nytimes_search.py
```

Type a search term, or `exit` to close the program.

## GUI

Run the desktop GUI:

```powershell
python nytimes_gui.py
```

Search articles, select a result, then double-click it or use `Open in browser`.

## Project Files

- `nytimes_search.py`: command-line version and API helper functions.
- `nytimes_gui.py`: desktop GUI.
- `.env.example`: example API key configuration.
- `requirements.txt`: Python dependency list.

## License

MIT
