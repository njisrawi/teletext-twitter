# teletext-twitter - creates pages for vbit2 teletext system
# (c) Mark Pentler 2018 (https://github.com/mpentler)
# see README.md for details on getting it running

import twitter
import time
import sys
import textwrap

# Read config.py for our access keys etc
config = {}
exec(open("config.py").read(), config)
twitter = twitter.Api(access_token_key = config["access_key"],
                      access_token_secret = config["access_secret"],
                      consumer_key = config["consumer_key"],
                      consumer_secret = config["consumer_secret"],
                      sleep_on_rate_limit = True) # so we don't hit the rate limit and raise an exception

def write_header():
    with open("/home/pi/teletext/P153.tti", "w+") as file:
        file.write("DE,Teletext Twitter\r\n")
        file.write("PN,15300\r\n")
        file.write("SC,0000\r\n")
        file.write("PS,8000\r\n")
        file.write("OL,0,Teletext Twitter\r\n")
        # graphical banner here - but not too big!

def write_timeline(): # grab the latest timeline
    statuses = twitter.GetHomeTimeline(count = 1)
    line_position = 1

    for status in statuses: # iterate through our responses
        tweet_time = time.strptime(status.created_at,"%a %b %d %H:%M:%S +0000 %Y")
        tweet_human_time = time.strftime("%d-%b-%Y %H:%S", tweet_time) # reformat time/date output
        tweet_username = status.user.screen_name
        tweet_text = textwrap.wrap(status.text, 40)

        with open("/home/pi/teletext/P153.tti", "a") as file:
            file.write("OL,{},{} | @{}".format(str(line_position), tweet_human_time, tweet_username) + "`" * (36-len(tweet_human_time)-len(tweet_username)) + "\r\n")
            line_position += 1
            for line in tweet_text:
                file.write("OL,{},{}\r\n".format(str(line_position), line))
                line_position += 1

def main():
    print("[*] teletext-twitter - (c) 2018 Mark Pentler (https://github.com/mpentler)", file=sys.stdout)
    print("[*] Beginning timeline scraping", file=sys.stdout)

    # for now we'll update for 30 seconds - may want to make this changeable?
    while True:
        write_header()
        write_timeline()
        print("[*] Waiting 30 seconds until next scrape", file=sys.stdout)
        time.sleep(30)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("[!] Interrupted by user. Exiting...", file=sys.stdout)
        sys.exit(0)
