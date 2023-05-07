import re


class ReadLogs:
    def __init__(self):
        self.logs = []
        self.filtered_logs = []

    def read(self, file_name):
        with open(file_name, "r") as file:
            lines = file.readlines()
            self.logs = [line.strip() for line in lines]
        return self.logs

    def filter_logs(self, logs, date_start, date_end):
        filtered_logs = []
        for log in logs:
            result = self.parse_log(log.strip())
            if date_start <= result["timestamp"].split("-")[0] <= date_end:
                filtered_logs.append(log)
        return filtered_logs

    @staticmethod
    def parse_log(line):
        try:
            log_pattern = r"^(\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2})\s(\S+)\s(\S+)\[(\d+)\]:\s(.*)$"
            match = re.match(log_pattern, line)
            if not match:
                return {}
            return {
                "timestamp": match.group(1),
                "hostname": match.group(2),
                "application": match.group(3),
                "pid_number": match.group(4),
                "message": match.group(5)
            }
        except Exception:
            raise Exception("Error while parsing log line")
