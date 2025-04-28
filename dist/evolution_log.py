import os
import json
import datetime

# Configuration
EVOLUTION_LOG = "jdss.json"

# Initialize the evolution log if it doesn't exist
if not os.path.exists(EVOLUTION_LOG):
    with open(EVOLUTION_LOG, "w") as log_file:
        json.dump({"evolution": []}, log_file, indent=4)

# Ensure the evolution log is valid JSON
if os.path.exists(EVOLUTION_LOG):
    try:
        with open(EVOLUTION_LOG, "r") as log_file:
            json.load(log_file)
    except json.JSONDecodeError:
        with open(EVOLUTION_LOG, "w") as log_file:
            json.dump({"evolution": []}, log_file, indent=4)

def log_evolution(event):
    """Log an event to the evolution log."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(EVOLUTION_LOG, "r+") as log_file:
        data = json.load(log_file)
        data["evolution"].append({"timestamp": timestamp, "event": event})
        log_file.seek(0)
        json.dump(data, log_file, indent=4)

# Example usage
if __name__ == "__main__":
    log_evolution("Initialized Groqee evolution log.")
    print("Evolution log updated.")