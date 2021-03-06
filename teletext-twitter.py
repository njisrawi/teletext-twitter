# teletext-twitter - creates pages for vbit2 teletext system
# (c) Mark Pentler 2018 (https://github.com/mpentler)
# see README.md for details on getting it running or run with -h

import twitter
import time
import sys
import textwrap
import argparse

# define our control codes here for easy use later
ESCAPE = chr(27)
RED = ESCAPE + chr(65)
CYAN = ESCAPE + chr(70)
DOUBLE_HEIGHT = ESCAPE + chr(77)
MOSAIC_CYAN = ESCAPE + chr(86)

# Read config.py for our Twitter access keys etc
config = {}
exec(open("config.py").read(), config)
twitter_object = twitter.Api(access_token_key = config["access_key"],
                      access_token_secret = config["access_secret"],
                      consumer_key = config["consumer_key"],
                      consumer_secret = config["consumer_secret"],
                      sleep_on_rate_limit = True) # so we don't hit the rate limit and raise an exception

def write_header(): # write a header for the page and pop a nice banner at the top
    with open("/home/pi/teletext/P153.tti", "w+") as file:
        file.write("DE,Autogenerated by Teletext-Twitter\r\n")
        file.write("PN,15300\r\n")
        file.write("SC,0000\r\n")
        file.write("PS,8000\r\n")
        file.write("OL,1," + DOUBLE_HEIGHT + "TELETEXT TWITTER" + MOSAIC_CYAN + (chr(127) * 22) + "\r\n")
        file.write("OL,3," + MOSAIC_CYAN + (chr(35) * 39) + "\r\n")

def write_timeline(): # grab the latest timeline - only 5 tweets for now
    statuses = twitter_object.GetHomeTimeline(count = 5)
    line_position = 4

    for status in statuses: # iterate through our responses
        tweet_time = time.strptime(status.created_at,"%a %b %d %H:%M:%S +0000 %Y")
        tweet_human_time = time.strftime("%d-%b-%Y %H:%S", tweet_time) # reformat time/date output
        tweet_username = status.user.screen_name
        tweet_text = textwrap.wrap(status.text, 39) # make sure our lines fit on the screen

        if (line_position + len(tweet_text) + 1) > 24: # are we going to fill the page?
            break # yep! dump the last tweet!

        with open("/home/pi/teletext/P153.tti", "a") as file:
            file.write("OL,{},".format(str(line_position)) + ("`" * (36-len(tweet_human_time)-len(tweet_username))) + "@{}".format(tweet_username) + " | " + "{}".format(tweet_human_time) + "\r\n")
            line_position += 1
            for line in tweet_text:
                line = line.replace("’", "'") # replacing some problematic characters here
                line = line.replace("_", "-") # the teletext English character set doesn't
                line = line.replace("#", "_") # support a lot of things!
                file.write("OL,{},".format(str(line_position)) + RED + "{}\r\n".format(line))
                line_position += 1

def parse_args():
    parser = argparse.ArgumentParser(description="Reads your Twitter timeline and turns it into teletext pages for your Raspberry Pi.")
    parser.add_argument("-d", "--delay", type=int, default=60, help="seconds between timeline scrapes (minimum is 60 seconds - lower values have no effect)")
    parser.add_argument("-v", "--version", action="version", version="0.2")
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true", default=False, help="suppresses all output to the terminal except warnings and errors")
    args = parser.parse_args()
    args.delay = max(60, args.delay)
    return args

def main():
    args = parse_args()

    if not args.quiet:
        print("[*] teletext-twitter - (c) 2018 Mark Pentler (https://github.com/mpentler)", file=sys.stdout)
        print("[*] Beginning timeline scraping", file=sys.stdout)

    while True:
        try:
            write_header()
            write_timeline()
            if not args.quiet:
                print("[*] Page updated. Waiting {} seconds until next scrape".format(args.delay), file=sys.stdout)
        except OSError as e:
            print("[!] Error accessing teletext data file, exiting: {}".format(e.strerror), file=sys.stderr)
            sys.exit(1)
        except twitter.error.TwitterError as e:
            for error in e.message:
                if error['code'] == 32:
                    print("[!] Authentication error accessing Twitter. Check config.py file and make sure your tokens are correct.")
                    print("[!] Exiting...")
                    sys.exit(1)
                print("[!] Error accessing your Twitter timeline: {}".format(error['message']), file=sys.stderr)
                print("[!] Trying again after specified delay", file=sys.stderr)
        time.sleep(args.delay)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("[*] Interrupted by user. Exiting...", file=sys.stdout)
        sys.exit(0)
