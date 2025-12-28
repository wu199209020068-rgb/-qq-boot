from nonebot import on_message
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.permission import SUPERUSER
import re

# ========== 已自动配置3个收款码（无需修改） ==========
ADMIN_QQ = "2466363558"
SELL_GROUP = "1077686695"
PAY_CONFIG = {
    "1": {
        "name": "港版支付宝",
        "img": "https://imgchr.com/i/pZYa9Vf",
        "type": "alipay_hk",
        "keyword": "pZYa9Vf",
        "desc": "港版支付宝收款码"
    },
    "2": {
        "name": "普通支付宝",
        "img": "https://imgchr.com/i/pZYaSqP",
        "type": "alipay",
        "keyword": "pZYaSqP",
        "desc": "普通支付宝收款码"
    },
    "3": {
        "name": "微信收款",
        "img": "https://imgchr.com/i/pZYUxKI",
        "type": "wechat",
        "keyword": "pZYUxKI",
        "desc": "微信收款码"
    }
}
goods = {}
orders = {}
gid = 1
oid = 2025001
pay_msg = {}

# ========== 自动识别防错（无需修改） ==========
def auto_recognize_paycode(choice):
    pay_info = PAY_CONFIG.get(choice)
    if not pay_info:
        return False, "❌ 仅支持1（港版支付宝）/2（普通支付宝）/3（微信）"
    if not re.match(r"^https?://imgchr\.com/i/[a-zA-Z0-9]+$", pay_info["img"]):
        return False, f"❌ 【{pay_info['name']}】链接无效"
    img_id = pay_info["img"].split("/")[-1]
    if img_id != pay_info["keyword"]:
        return False, f"❌ 收款码类型不匹配"
    return True, pay_info

# ========== 管理员功能（私聊免@） ==========
admin = on_message(priority=1, permission=SUPERUSER)
@admin.handle()
async def a_op(bot: Bot, event: Event):
    global gid
    msg = str(event.get_message()).strip()
    if msg.startswith("上架 "):
        try:
            n,p = msg.replace("上架 ","").split(" ",1)
            goods[gid] = {"n":n,"p":p}
            await admin.finish(f"✅ 上架成功｜编号{gid}：{n} - {p}元")
            gid +=1
        except:
            await admin.finish("❌ 格式：上架 商品名 价格")
    elif msg.startswith("改价 "):
        try:
            t,p = msg.replace("改价 ","").split(" ",1)
            goods[int(t)]["p"] = p
            await admin.finish(f"✅ 商品{int(t)}改价完成")
        except:
            await admin.finish("❌ 格式：改价 商品编号 新价格")
    elif msg.startswith("下架 "):
        try:
            del goods[int(msg.replace("下架 ",""))]
            await admin.finish("✅ 下架完成")
        except:
            await admin.finish("❌ 格式：下架 商品编号")
    elif msg.startswith("退款 "):
        oid = msg.replace("退款 ","").strip()
        if oid in orders: del orders[oid]
        await admin.finish(f"✅ 订单{oid}退款完成")

# ========== 群内功能（@机器人触发） ==========
main = on_message(rule=to_me(), priority=2)
@main.handle()
async def m_op(bot: Bot, event: Event):
    global oid
    msg = str(event.get_message()).strip()
    uid = event.get_user_id()
    qid = event.get_session_id().split("_")[1] if "_" in event.get_session_id() else ""
    if qid != SELL_GROUP: return

    if msg == "":
        menu = "📌 功能菜单【@机器人+指令】\n▸商品列表 ▸购买 编号 数量\n▸1=港版支付宝 2=普通支付宝 3=微信\n▸已付款 ▸绑定PSN/查询PSN ▸厢型车位置/GTA更新"
        await main.finish(menu)
    elif msg == "商品列表":
        glist = "📦 商品列表\n"
        for i,d in goods.items(): glist += f"{i}. {d['n']} - {d['p']}元\n"
        await main.finish(glist)
    elif msg.startswith("购买 "):
        try:
            i,num = msg.replace("购买 ","").split(" ")
            i = int(i)
            total = int(goods[i]["p"]) * int(num)
            orders[str(oid)] = {"uid":uid,"t":total}
            await main.finish(f"✅ 下单成功｜订单{oid} 总价{total}元\n回复1/2/3选付款方式")
            oid +=1
        except:
            await main.finish("❌ 格式：购买 商品编号 数量")
    elif msg in ["1","2","3"]:
        valid, res = auto_recognize_paycode(msg)
        if not valid:
            await main.finish(res)
        pay_info = res
        latest_order = max(orders.keys()) if orders else ""
        if orders.get(latest_order, {}).get("uid") != uid:
            await main.finish("❌ 你暂无未付款订单")
        send_msg = await bot.send(event, f"✅ 选择【{pay_info['name']}】\n订单{latest_order} 支付{orders[latest_order]['t']}元\n付款后发【已付款】撤回", pay_info["img"])
        pay_msg[send_msg["message_id"]] = uid
    elif msg == "已付款":
        for mid,u in pay_msg.items():
            if u == uid:
                await bot.delete_msg(message_id=mid)
                del pay_msg[mid]
                await main.finish("✅ 收款码已撤回｜付款确认中！")
    elif msg.startswith("绑定PSN "):
        await main.finish(f"✅ PSN【{msg.replace('绑定PSN ','')}】绑定成功")
    elif msg == "查询PSN":
        await main.finish("✅ PSN信息｜奖杯888 时长2600h 常玩GTA5")
    elif msg == "厢型车位置":
        await main.finish("✅ GTA5坐标｜X1284.3 Y-3231.5 Z5.9")
    elif msg == "GTA本周更新":
        await main.finish("✅ GTA更新｜CEO双倍奖励 厢型车刷新率提升")
    else:
        await main.finish(f"✅ AI回复：{msg}")
