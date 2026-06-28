# run_all.py

import os

# list of scripts to run (in order)
SCRIPTS = [
    "load_data.py",
    "clean_data.py",
    "analysis_stats.py",
    "build_index.py",
    "summary_report.py"
]


def main():
    print("starting full pipeline...\n")

    for script in SCRIPTS:
        path = os.path.join("src", script)
        print("running:", script)

        cmd = f"python {path}"
        exit_code = os.system(cmd)

        if exit_code != 0:
            print("error running:", script)
            return

        print("done:", script)
        print("----------------------------")

    print("\nall tasks completed.")


if __name__ == "__main__":
    main()
