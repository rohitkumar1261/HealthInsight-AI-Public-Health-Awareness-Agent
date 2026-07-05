# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     https://www.apache.org/licenses/LICENSE-2.0

import uvicorn
import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open("http://127.0.0.1:8000/")

if __name__ == "__main__":
    print("Starting Public Health Awareness Agent Dashboard on http://127.0.0.1:8000/")
    # Automatically open the browser tab after 1.5 seconds
    Timer(1.5, open_browser).start()
    
    # Run the uvicorn web server
    uvicorn.run("app.web_server:app", host="0.0.0.0", port=8000, reload=True)
