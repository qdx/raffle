# -*- coding: utf-8 -*-

import json
import secrets
import sys
import time
from cmd import Cmd
from datetime import datetime
from select import select

from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import prompt
from prompt_toolkit import shortcuts

from tickets import tickets

DISABLED_KEY = "disabled"

"""
Data schema:
    {
        "<code>": {
            "name": "<name>",
            "time": "<iso time string>",
            "disabled": "<True|False>"
        }
    }
"""


def load_data():
    with open("./data", "r") as f:
        return json.load(f)


def save_data(d):
    with open("./data", "w") as f:
        return json.dump(d, f)


class MyPrompt(Cmd):
    prompt = '$dx> '
    intro = "欢迎使用dx抽奖系统！输入'?'获得帮助"

    def do_raffle(self, stub):
        '''Execute raffle!'''
        shortcuts.clear()
        data = load_data()
        self.summary(data)

        cont = ""
        while cont != "yes" and cont != "no":
            cont = prompt('是否确认在以上参与人员中进行抽奖？(yes/no)').strip()

        candidates = []
        for k in data.keys():
            if DISABLED_KEY in data[k] and data[k][DISABLED_KEY]:
                continue
            candidates.append(k)

        if cont == "yes":
            shortcuts.clear()
            while True:
                timeout = 0.01
                chosen = secrets.choice(candidates)
                print(f"{data[chosen]['name']}, {chosen}")
                rlist, _, _ = select([sys.stdin], [], [], timeout)
                if rlist:
                    s = sys.stdin.readline()
                    contents = ["获奖", "者", "出", "现", "了", "！！！", "Ta", "就是："]

                    for c in contents:
                        print(c)
                        time.sleep(0.5)

                    print(f"{data[chosen]['name']}, {chosen}")
                    data[chosen][DISABLED_KEY] = True
                    save_data(data)
                    break

    def do_exit(self, inp):
        '''Exit the application.'''
        print("Bye")
        return True

    def do_release(self, code):
        '''Release a redeemed code'''
        if code not in tickets:
            print("Not a valid code, ignore")
            return

        data = load_data()
        if code not in data:
            print("Code not redeemed, ignore")
            return

        del data[code]
        save_data(data)
        print(f"Code:{code} released.")

    def do_enable(self, code):
        '''Enable certain code if disabled'''
        if code not in tickets:
            print("Not a valid code, ignore")
            return

        data = load_data()
        if code not in data:
            print("Code not redeemed, nothing to do.")
            return
        if DISABLED_KEY not in data[code] or not data[code][DISABLED_KEY]:
            print("Code is active, nothing to do")
            return

        data[code][DISABLED_KEY] = False
        save_data(data)
        print(f"Code:{code} is enable for {data[code]['name']}")

    def do_disable(self, code):
        '''Disable certain code'''
        if code not in tickets:
            print("Not a valid code, ignore")
            return

        data = load_data()
        if code not in data:
            data[code] = {}
            data[code]["name"] = "invalid"

        data[code]["time"] = datetime.now().isoformat(sep="T", timespec="milliseconds")
        data[code][DISABLED_KEY] = True
        save_data(data)
        print(f"Code: {code} disabled!")

    def do_check(self, code):
        '''Check status of a redeem code.'''
        data = load_data()
        if code not in tickets:
            print("Invalid code!")
            return

        if code in data:
            print(f"Code redeemed by:{data[code]['name']} at {data[code]['time']}")
            return

        print("Code still usable")

    def do_clear(self, stub):
        '''Clear screen'''
        shortcuts.clear()

    def summary(self, data, show_code=False):
        count = len(data.items())
        prob = 1.0 / count * 100 if count != 0 else 100
        print(f"目前参与抽奖人数：{count}, 中奖概率：{str(prob)[:4]}%")
        print(f"以下是目前参与人员:")
        for k in data.keys():
            if DISABLED_KEY in data[k] and data[k][DISABLED_KEY]:
                continue
            if show_code:
                print(f"Code:{k}, Name:{data[k]['name']}")
            else:
                print(f"Name:{data[k]['name']}")

    def do_clearall(self, stub):
        '''Clear all check in data'''
        ans = prompt('This will clear all candidiates data, not recoverable, are you sure? (Sure):')
        if ans == "Sure":
            save_data({})
            print("Data cleared!")
        else:
            print("Data not touched")

    def do_list(self, stub):
        '''List all participants'''
        shortcuts.clear()
        data = load_data()
        for k in data.keys():
            d = "active"
            if DISABLED_KEY in data[k] and data[k][DISABLED_KEY]:
                d = DISABLED_KEY

            print(f"Code:{k}, Name:{data[k]['name']}, Last update at:{data[k]['time']}, status:{d}")

    def count(self):
        data = load_data()
        count = 0
        for k in data.keys():
            if data[k][DISABLED_KEY]:
                continue
            count += 1
        return count

    def do_col(self, inp):
        '''Enter collection mode to collect names for the raffle.'''
        shortcuts.clear()
        data = load_data()
        self.summary(data)
        count = self.count()

        redeemed_codes = data.keys()

        name = ""
        while name.strip() != "#q":
            name = prompt('欢迎光临！请输入您的姓名:')
            if len(name) > 100:
                print("您的名字太长了，俺记不住，麻烦您用个短一点的。")
                continue

            code = prompt('请输入你的4位验证码(请找邀请人索取):')
            clean_code = code.strip()
            if len(clean_code) > 4:
                print("验证码只有四位噢")
                continue

            if clean_code in redeemed_codes:
                print("您输入的验证码已被兑换！")
                continue

            if clean_code not in tickets:
                print("您输入的验证码无效噢！")
                continue

            data[clean_code] = {}
            data[clean_code]["name"] = name
            data[clean_code]["time"] = datetime.now().isoformat(sep="T", timespec="milliseconds")
            data[clean_code][DISABLED_KEY] = False
            save_data(data)

            count = self.count()
            new_prob = 1.0 / (count) * 100
            print(f"欢迎 {name} 大驾光临！")
            time.sleep(0.5)
            print(f"您是第{count}个参与者,")
            time.sleep(0.5)
            print(f"目前的中奖概率是{new_prob}%")
            time.sleep(0.5)
            print("您可以入场就座了 :)")
            secs = 5
            for i in range(secs):
                print(f"{secs - i}秒后系统将为下一位客人进行服务。")
                time.sleep(1)
            shortcuts.clear()
            name = ""
            code = ""


MyPrompt().cmdloop()
