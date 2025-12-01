import argparse
import json
import os
from datetime import datetime

# ============================================================
#  CSV PARSING + VALIDATION
# ============================================================
def parse_csv_file(path):
    valid_flights = []
    error_entries = []

    with open(path, "r", encoding="utf-8") as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = raw_line.strip()

            # Blank line
            if line == "":
                continue

            # Comment line
            if line.startswith("#"):
                error_entries.append(
                    f"Line {line_number}: {line} → comment line, ignored for data parsing"
                )
                continue

            # Header line
            if line.startswith("flight_id"):
                continue

            parts = line.split(",")

            # Must have 6 fields
            if len(parts) != 6:
                error_entries.append(
                    f"Line {line_number}: {line} → missing required fields"
                )
                continue

            flight_id, origin, destination, dep_str, arr_str, price_str = parts
            reasons = []

            # flight_id validation
            if not (2 <= len(flight_id) <= 8 and flight_id.isalnum()):
                reasons.append("invalid flight_id")

            # airport code validation
            def check_airport(code, field_name):
                if len(code) != 3 or not code.isupper():
                    return f"invalid {field_name} code"
                if code == "XXX":
                    return f"invalid {field_name} code"
                return None

            r = check_airport(origin, "origin")
            if r:
                reasons.append(r)
            r = check_airport(destination, "destination")
            if r:
                reasons.append(r)

            # datetime validation
            try:
                dep_dt = datetime.strptime(dep_str, "%Y-%m-%d %H:%M")
            except:
                dep_dt = None
                reasons.append("invalid departure datetime")

            try:
                arr_dt = datetime.strptime(arr_str, "%Y-%m-%d %H:%M")
            except:
                arr_dt = None
                reasons.append("invalid arrival datetime")

            if dep_dt and arr_dt and arr_dt <= dep_dt:
                reasons.append("arrival before departure")

            # price validation
            try:
                price = float(price_str)
                if price <= 0:
                    reasons.append("negative price value")
            except:
                reasons.append("invalid price")

            # VALID / INVALID
            if len(reasons) == 0:
                valid_flights.append(
                    {
                        "flight_id": flight_id,
                        "origin": origin,
                        "destination": destination,
                        "departure_datetime": dep_str,
                        "arrival_datetime": arr_str,
                        "price": float(price_str),
                    }
                )
            else:
                reason_text = ", ".join(reasons)
                error_entries.append(
                    f"Line {line_number}: {line} → {reason_text}"
                )

    return valid_flights, error_entries


# ============================================================
#  MAIN PROGRAM
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Flight Schedule Parser and Query Tool")

    parser.add_argument("-i", help="Parse a single CSV file")
    parser.add_argument("-d", help="Parse all CSV files inside a folder")
    parser.add_argument("-o", help="Output JSON path for valid flights (optional)")
    parser.add_argument("-j", help="Load an existing JSON database instead of parsing CSV")
    parser.add_argument("-q", help="Query JSON file to apply filters on database")

    args = parser.parse_args()

    all_valid = []
    all_errors = []

    # ------------------------------------------------
    # LOAD EXISTING JSON DATABASE (-j)
    # ------------------------------------------------
    if args.j:
        try:
            with open(args.j, "r", encoding="utf-8") as f:
                all_valid = json.load(f)
            print("Loaded existing database from", args.j)
        except:
            print("Error: Could not load JSON database.")
            return

    # ------------------------------------------------
    # PARSE SINGLE CSV (-i)
    # ------------------------------------------------
    if args.i and not args.j:
        valid, errors = parse_csv_file(args.i)
        all_valid.extend(valid)
        all_errors.extend(errors)

    # ------------------------------------------------
    # PARSE FOLDER (-d)
    # ------------------------------------------------
    if args.d and not args.j:
        for filename in os.listdir(args.d):
            if filename.endswith(".csv"):
                path = os.path.join(args.d, filename)
                valid, errors = parse_csv_file(path)
                all_valid.extend(valid)
                all_errors.extend(errors)

    # ------------------------------------------------
    # RUN QUERIES (-q)
    # ------------------------------------------------
    if args.q:
        with open(args.q, "r", encoding="utf-8") as f:
            queries = json.load(f)

        # If single query object, wrap it into list
        if isinstance(queries, dict):
            queries = [queries]

        responses = []

        # Helper to convert datetime string
        def to_dt(x):
            return datetime.strptime(x, "%Y-%m-%d %H:%M")

        for q in queries:
            matches = []

            for flight in all_valid:
                ok = True

                for key, value in q.items():

                    # Exact matches
                    if key in ["flight_id", "origin", "destination"]:
                        if flight[key] != value:
                            ok = False

                    # Price ≤ value
                    elif key == "price":
                        if flight["price"] > value:
                            ok = False

                    # departure >= query
                    elif key == "departure_datetime":
                        if to_dt(flight["departure_datetime"]) < to_dt(value):
                            ok = False

                    # arrival <= query
                    elif key == "arrival_datetime":
                        if to_dt(flight["arrival_datetime"]) > to_dt(value):
                            ok = False

                if ok:
                    matches.append(flight)

            responses.append({
                "query": q,
                "matches": matches
            })

        # Save response file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"response_123456_Nisa_Yakut_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(responses, f, indent=2)

        print("Query results saved to:", filename)

    # ------------------------------------------------
    # WRITE OUTPUT FILES (ONLY IF CSV PARSED)
    # ------------------------------------------------
    if not args.j:
        # errors.txt
        with open("errors.txt", "w", encoding="utf-8") as f:
            for e in all_errors:
                f.write(e + "\n")

        # db.json
        output_path = args.o if args.o else "db.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_valid, f, indent=2)

        print("Parsing completed.")
        print("Valid flights saved to:", output_path)
        print("Errors saved to: errors.txt")


if __name__ == "__main__":
    main()
