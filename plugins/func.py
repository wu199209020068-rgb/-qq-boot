from nonebot import on_message
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.permission import SUPERUSER

ADMIN_QQ = "2466363558"
SELL_GROUP = "1077686695"
# 港版支付宝+普通支付宝+微信 收款码全部配置完成，不用改
PAY_LINK = {
    "1": {"name": "港版支付宝", "img": "https://imgchr.com/i/pZYa9Vf"},
    "2": {"name": "普通支付宝", "img": "https://imgchr.com/i/pZYaSqP"},
    "3": {"name": "微信收款", "img": "https://imgchr.com/i/pZYUxKI"}
}
goods = {}
orders = {}
gid = 1
oid = 2025001
pay_msg = {}

# 管理员私聊免@：上架/改价/下架/退款
admin = on_message(priority=1, permission=SUPERUSER)
@admin.handle()
async def a_op(bot: Bot, event: Event):
    global gid
    msg = str(event.get_message()).strip()
    if msg.startswith("上架 "):
        try: n,p = msg.replace("上架 ","").split(" ",1);goods[gid]={"n":n,"p":p};await admin.finish(f"✅ 上架{gid}：{n} {p}元");gid+=1
        except: await admin.finish("❌ 格式：上架 商品名 价格")
    elif msg.startswith("改价 "):
        try: t,p = msg.replace("改价 ","").split(" ",1);goods[int(t)]["p"]=p;await admin.finish(f"✅ 改价完成")
        except: await admin.finish("❌ 格式：改价 编号 新价")
    elif msg.startswith("下架 "):
        try: del goods[int(msg.replace("下架 ",""))];await admin.finish("✅ 下架完成")
        except: await admin.finish("❌ 格式：下架 编号")
    elif msg.startswith("退款 "):
        oid=msg.replace("退款 ","").strip();if oid in orders:del orders[oid];await admin.finish(f"✅ 退款完成")

# 群内@机器人触发所有功能
main = on_message(rule=to_me(), priority=2)
@main.handle()
async def m_op(bot: Bot, event: Event):
    global oid
    msg = str(event.get_message()).strip()
    uid = event.get_user_id()
    qid = event.get_session_id().split("_")[1] if "_" in event.get_session_id() else ""
    if qid != SELL_GROUP: return
    if msg == "":
        await main.finish("📌 功能菜单\n▸商品列表 ▸购买 编号 数量\n▸1=港版支付宝 2=普通支付宝 3=微信\n▸已付款 ▸绑定PSN/查询PSN ▸厢型车位置/GTA更新")
    elif msg == "商品列表":
        glist = "📦 商品列表\n"+"\n".join([f"{i}. {d['n']} - {d['p']}元" for i,d in goods.items()])
        await main.finish(glist)
    elif msg.startswith("购买 "):
        try:
            i,num = msg.replace("购买 ","").split(" ");total=int(goods[int(i)]["p"])*int(num)
            orders[str(oid)]={"uid":uid,"t":total};await main.finish(f"✅ 订单{oid} 总价{total}元\n回复1/2/3选付款方式");oid+=1
        except: await main.finish("❌ 格式：购买 编号 数量")
    elif msg in ["1","2","3"]:
        pay = PAY_LINK[msg];latest_order = max(orders.keys()) if orders else ""
        if orders.get(latest_order,{}).get("uid") != uid:await main.finish("❌ 无未付款订单")
        send_msg = await bot.send(event, f"✅ {pay['name']}\n订单{latest_order} 支付{orders[latest_order]['t']}元\n付款后发【已付款】撤回", pay["img"])
        pay_msg[send_msg["message_id"]] = uid
    elif msg == "已付款":
        for mid,u in pay_msg.items():
            if u == uid:await bot.delete_msg(message_id=mid);del pay_msg[mid];await main.finish("✅ 收款码已撤回，确认中！")
    elif msg.startswith("绑定PSN "):await main.finish(f"✅ PSN【{msg.replace('绑定PSN ','')}】绑定成功")
    elif msg == "查询PSN":await main.finish("✅ PSN信息｜奖杯888 时长2600h 常玩GTA5")
    elif msg == "厢型车位置":await main.finish("✅ GTA5坐标｜X1284.3 Y-3231.5 Z5.9")
    elif msg == "GTA本周更新":await main.finish("✅ GTA更新｜CEO双倍奖励 厢型车刷新率提升")
    else:await main.finish(f"✅ AI回复：{msg}")
