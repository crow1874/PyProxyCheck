# Developer: 乌鸦 (Crow) | Telegram: https://t.me/cfwuya1
import time
import socket
import random
import string
import asyncio
import re
from typing import List, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
from aiohttp.abc import AbstractResolver
from netaddr import IPNetwork, IPAddress

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOC_MAP = {
    "CN": "中国", "TW": "台湾", "HK": "香港", "MO": "澳门", "US": "美国", "JP": "日本",
    "KR": "韩国", "GB": "英国", "DE": "德国", "FR": "法国", "RU": "俄罗斯", "SG": "新加坡",
    "MY": "马来西亚", "TH": "泰国", "VN": "越南", "PH": "菲律宾", "ID": "印度尼西亚",
    "IN": "印度", "AU": "澳大利亚", "CA": "加拿大", "BR": "巴西", "AR": "阿根廷",
    "ZA": "南非", "EG": "埃及", "TR": "土耳其", "SA": "沙特阿拉伯", "AE": "阿联酋",
    "IR": "伊朗", "IQ": "伊拉克", "IL": "以色列", "PK": "巴基斯坦", "BD": "孟加拉国",
    "LK": "斯里兰卡", "MM": "缅甸", "KH": "柬埔寨", "LA": "老挝", "KP": "朝鲜",
    "MN": "蒙古", "NP": "尼泊尔", "BT": "不丹", "MV": "马尔代夫", "KZ": "哈萨克斯坦",
    "UZ": "乌兹别克斯坦", "KG": "吉尔吉斯斯坦", "TJ": "塔吉克斯坦", "TM": "土库曼斯坦",
    "AF": "阿富汗", "AZ": "阿塞拜疆", "GE": "格鲁吉亚", "AM": "亚美尼亚", "UA": "乌克兰",
    "BY": "白俄罗斯", "MD": "摩尔多瓦", "PL": "波兰", "CZ": "捷克", "SK": "斯洛伐克",
    "HU": "匈牙利", "AT": "奥地利", "CH": "瑞士", "LI": "列支敦士登", "NL": "荷兰",
    "BE": "比利时", "LU": "卢森堡", "IE": "爱尔兰", "DK": "丹麦", "SE": "瑞典",
    "NO": "挪威", "FI": "芬兰", "IS": "冰岛", "ES": "西班牙", "PT": "葡萄牙",
    "IT": "意大利", "VA": "梵蒂冈", "SM": "圣马力诺", "GR": "希腊", "CY": "塞浦路斯",
    "MT": "马耳他", "AL": "阿尔巴尼亚", "MK": "北马其顿", "BG": "保加利亚", "RO": "罗马尼亚",
    "RS": "塞尔维亚", "HR": "克罗地亚", "SI": "斯洛文尼亚", "BA": "波黑", "ME": "黑山",
    "XK": "科索沃", "EE": "爱沙尼亚", "LV": "拉脱维亚", "LT": "立陶宛", "MX": "墨西哥",
    "CL": "智利", "CO": "哥伦比亚", "PE": "秘鲁", "VE": "委内瑞拉", "EC": "厄瓜多尔",
    "BO": "玻利维亚", "PY": "巴拉圭", "UY": "乌拉圭", "GY": "圭亚那", "SR": "苏里南",
    "CU": "古巴", "JM": "牙买加", "HT": "海地", "DO": "多米尼加", "PA": "巴拿马",
    "CR": "哥斯达黎加", "NI": "尼加拉瓜", "HN": "洪都拉斯", "SV": "萨尔瓦多", "GT": "危地马拉",
    "BZ": "伯利兹", "BS": "巴哈马", "BB": "巴巴多斯", "TT": "特立尼达和多巴哥", "NZ": "新西兰",
    "FJ": "斐济", "PG": "巴布亚新几内亚", "SB": "所罗门群岛", "VU": "瓦努阿图", "WS": "萨摩亚",
    "TO": "汤加", "MA": "摩洛哥", "DZ": "阿尔及利亚", "TN": "突尼斯", "LY": "利比亚",
    "SD": "苏丹", "SS": "南苏丹", "ET": "埃塞俄比亚", "KE": "肯尼亚", "TZ": "坦桑尼亚",
    "UG": "乌干达", "RW": "卢旺达", "BI": "布隆迪", "SO": "索马里", "DJ": "吉布提",
    "ER": "厄立特里亚", "MZ": "莫桑比克", "MG": "马达加斯加", "SC": "塞舌尔", "MU": "毛里求斯",
    "ZM": "赞比亚", "ZW": "津巴布韦", "MW": "马拉维", "AO": "安哥拉", "NA": "纳米比亚",
    "BW": "博茨瓦纳", "SZ": "斯威士兰", "LS": "莱索托", "NG": "尼日利亚", "GH": "加纳",
    "CI": "科特迪瓦", "SN": "塞内加尔", "ML": "马里", "BF": "布基纳法索", "NE": "尼日尔",
    "TG": "多哥", "BJ": "贝宁", "LR": "利比里亚", "SL": "塞拉利昂", "GN": "几内亚",
    "GW": "几内亚比绍", "GM": "冈比亚", "CV": "佛得角", "CM": "喀麦隆", "GA": "加蓬",
    "CG": "刚果(布)", "CD": "刚果(金)", "GQ": "赤道几内亚", "TD": "乍得", "CF": "中非",
    "ST": "圣多美和普林西比", "QA": "卡塔尔", "KW": "科威特", "BH": "巴林", "OM": "阿曼",
    "YE": "也门", "JO": "约旦", "LB": "黎巴嫩", "SY": "叙利亚", "PS": "巴勒斯坦",
    "AD": "安道尔", "MC": "摩纳哥", "FO": "法罗群岛", "GL": "格陵兰", "BM": "百慕大",
    "KY": "开曼群岛", "VG": "英属维尔京群岛", "VI": "美属维尔京群岛", "PR": "波多黎各", "GU": "关岛",
    "MP": "北马里亚纳群岛", "AS": "美属萨摩亚", "AW": "阿鲁巴", "CW": "库拉索", "SX": "荷属圣马丁",
    "RE": "留尼汪", "GP": "瓜德罗普", "MQ": "马提尼克", "GF": "法属圭亚那", "NC": "新喀里多尼亚",
    "PF": "法属波利尼西亚"
}

CF_IPV4 = [
    "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22",
    "141.101.64.0/18", "108.162.192.0/18", "190.93.240.0/20", "188.114.96.0/20",
    "197.234.240.0/22", "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13",
    "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22"
]
CF_IPV6 = [
    "2400:cb00::/32", "2606:4700::/32", "2803:f800::/32", "2405:b500::/32",
    "2405:8100::/32", "2a06:98c0::/29", "2c0f:f248::/32"
]

class SingleIPResolver(AbstractResolver):
    def __init__(self, target_ip, target_port):
        self.target_ip = target_ip
        self.target_port = target_port
    async def resolve(self, host, port=0, family=socket.AF_INET):
        return [{'hostname': host, 'host': self.target_ip, 'port': self.target_port, 'family': family, 'proto': 0, 'flags': 0}]
    async def close(self):
        pass

def check_is_cf_official(ip_str):
    try:
        ip = IPAddress(ip_str)
        cidrs = CF_IPV6 if ip.version == 6 else CF_IPV4
        for cidr in cidrs:
            if ip in IPNetwork(cidr): return True
        return False
    except: return False

def parse_trace(text):
    data = {}
    for line in text.split('\n'):
        parts = line.split('=', 1)
        if len(parts) == 2: data[parts[0].strip()] = parts[1].strip()
    return data

async def test_connection(session, ip, port, proto, host_header, path="/cdn-cgi/trace", target_host=None, retries=1):
    if not target_host: target_host = host_header 
    url = f"{proto}://{target_host}{path}"
    headers = {"Host": host_header, "User-Agent": "Mozilla/5.0"}
    for attempt in range(retries + 1):
        try:
            async with session.get(url, headers=headers, timeout=5, allow_redirects=False) as response:
                text = await response.text()
                return response.status, text
        except Exception as e:
            if attempt == retries: return 0, str(e)
            await asyncio.sleep(0.2)
    return 0, "Timeout"

def get_loc_name(code):
    if not code: return "未知"
    return LOC_MAP.get(code.upper(), code)

async def check_single_ip(ip_part: str, port: int, original_input: str) -> Dict[str, Any]:
    full_address = f"{ip_part}:{port}"
    if ":" in ip_part and not ip_part.startswith("["): full_address = f"[{ip_part}]:{port}"
    if check_is_cf_official(ip_part):
        return {"错误": "这是cloudflare官方IP", "地址": full_address, "原始输入": original_input}
    
    is_https_port = port in [443, 8443, 2053, 2083, 2087, 2096, 43]
    protocols = ["https"] if is_https_port else ["http"]
    if port == 43: protocols = ["https", "http"]
    
    resolver = SingleIPResolver(ip_part, port)
    connector = aiohttp.TCPConnector(resolver=resolver, ssl=False, limit=0)
    last_error_loc = ""
    
    async with aiohttp.ClientSession(connector=connector) as session:
        for proto in protocols:
            status, text = await test_connection(session, ip_part, port, proto, "trace.cloudflare.com")
            if status == 200 and "colo=" in text:
                trace = parse_trace(text)
                loc_code = trace.get("loc", "")
                speed_status, _ = await test_connection(session, ip_part, port, proto, "speed.cloudflare.com", "/__down?bytes=50", "speed.cloudflare.com", retries=1)
                if speed_status != 200:
                    last_error_loc = loc_code
                    continue
                random_host = ''.join(random.choices(string.ascii_lowercase, k=10)) + ".com"
                trap_status, trap_text = await test_connection(session, ip_part, port, proto, random_host, "/cdn-cgi/trace", retries=0)
                if trap_status == 200 and "colo=" in trap_text:
                    last_error_loc = loc_code
                    break
                return {"状态": "有效的 Proxyip", "地址": full_address, "地区": get_loc_name(loc_code), "原始输入": original_input}
    
    final_loc = get_loc_name(last_error_loc) if last_error_loc else "未知"
    return {"状态": "无效", "地址": full_address, "地区": final_loc, "原始输入": original_input}

async def resolve_and_check(user_input: str):
    clean_input = user_input.strip()
    clean_input = re.sub(r'^https?://', '', clean_input, flags=re.IGNORECASE)
    clean_input = clean_input.rstrip('/')
    host = ""
    port = 443 
    if clean_input.startswith("["):
        match = re.match(r"^\[(.*?)\](?::(\d+))?$", clean_input)
        if match:
            host = match.group(1)
            if match.group(2): port = int(match.group(2))
        else: host = clean_input
    elif ":" in clean_input:
        if clean_input.count(":") > 1: host = clean_input 
        else:
            parts = clean_input.rsplit(":", 1)
            host = parts[0]
            if parts[1].isdigit(): port = int(parts[1])
            else: host = clean_input
    else: host = clean_input
    
    unique_ips = set()
    try:
        socket.inet_pton(socket.AF_INET, host)
        unique_ips.add(host) 
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, host)
            unique_ips.add(host) 
        except socket.error:
            loop = asyncio.get_event_loop()
            try:
                infos = await loop.getaddrinfo(host, None)
                for info in infos: unique_ips.add(info[4][0])
            except Exception: pass 
    
    if not unique_ips:
        return [{"状态": "无效", "地址": f"{host}:{port}", "地区": "域名解析失败", "原始输入": clean_input}]

    tasks = [check_single_ip(str(ip), port, clean_input) for ip in unique_ips]
    results = await asyncio.gather(*tasks)
    return results

@app.get("/", response_class=HTMLResponse)
async def home_page():
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>全能 IP/域名 检测</title>
<style>
body{margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;background-image:url('https://bing.biturl.top/?resolution=1920&format=image&index=0&mkt=zh-CN');background-size:cover;background-position:center;background-attachment:fixed;background-repeat:no-repeat;color:#fff}
body::before{content:"";position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.4);z-index:-1}
.glass-container{background:rgba(0,0,0,0.65);border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,0.3);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.15);padding:40px;width:90%;max-width:500px;text-align:center;color:white;margin:20px 0;position:relative;z-index:1}
h1{margin-bottom:15px;font-weight:400;text-shadow:0 2px 4px rgba(0,0,0,0.5);letter-spacing:1px}
p.hint{font-size:13px;margin-bottom:24px;opacity:0.8;color:#ddd}
input{width:100%;padding:14px 0;margin-bottom:20px;border:1px solid rgba(255,255,255,0.2);border-radius:8px;background:rgba(255,255,255,0.1);font-size:16px;text-align:center;outline:none;box-sizing:border-box;transition:all 0.3s;color:#fff}
input:focus{background:rgba(255,255,255,0.2);border-color:rgba(255,255,255,0.5);box-shadow:0 0 15px rgba(255,255,255,0.1)}
input::placeholder{color:rgba(255,255,255,0.5)}
button{width:100%;padding:14px;border:none;border-radius:8px;background:linear-gradient(135deg,#3b82f6 0%,#2563eb 100%);color:white;font-size:16px;cursor:pointer;transition:all 0.3s;font-weight:600;letter-spacing:1px;box-shadow:0 4px 6px rgba(0,0,0,0.2)}
button:hover{background:linear-gradient(135deg,#2563eb 0%,#1d4ed8 100%);transform:translateY(-2px)}
.result-section{margin-top:25px;text-align:left;display:none}
.section-title{font-size:13px;margin-bottom:12px;padding-bottom:5px;border-bottom:1px solid rgba(255,255,255,0.2);font-weight:bold;text-transform:uppercase;letter-spacing:1px}
.result-card{background:rgba(255,255,255,0.08);border-radius:8px;padding:12px;margin-bottom:10px;font-size:14px;line-height:1.6;transition:all 0.3s;border-left:4px solid transparent}
.result-card.valid{background:rgba(46,204,113,0.15);border-left-color:#2ecc71}
.result-card.invalid{background:rgba(231,76,60,0.15);border-left-color:#e74c3c}
.result-row{display:flex;justify-content:space-between}
.label{opacity:0.7;margin-right:10px;font-size:13px}
.val{font-weight:bold;text-shadow:0 1px 2px rgba(0,0,0,0.5)}
.status-text-ok{color:#4ade80}
.status-text-fail{color:#f87171}
.loading{margin-top:20px;font-style:italic;opacity:0.9;color:#aaa}
.github-link{position:absolute;top:20px;right:20px;color:rgba(255,255,255,0.8);z-index:10;transition:all 0.3s}
.github-link:hover{color:#fff;transform:scale(1.1)}
.github-link svg{width:32px;height:32px}
</style>
</head>
<body>
<a href="https://github.com/crow1874/PyProxyCheck" target="_blank" class="github-link" title="在 GitHub 上查看源码">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
</a>
<div class="glass-container">
<h1>全能 IP/域名 检测</h1>
<p class="hint">支持 IPv4 / IPv6 / 域名 / 网址 (自动识别端口)</p>
<input type="text" id="ipInput" placeholder="请输入 (例如 google.com 或 1.1.1.1:80)">
<button onclick="checkIP()">立即查询</button>
<div id="loader" class="loading" style="display:none;">正在解析并检测，请稍候...</div>
<div id="validSection" class="result-section">
<div class="section-title" style="color:#4ade80;">检测成功 (有效)</div>
<div id="validList"></div>
</div>
<div id="invalidSection" class="result-section">
<div class="section-title" style="color:#f87171;">检测失败 (无效)</div>
<div id="invalidList"></div>
</div>
</div>
<script>
document.getElementById("ipInput").addEventListener("keypress",function(e){if(e.key==="Enter"){e.preventDefault();checkIP()}});
async function checkIP(){
const input=document.getElementById("ipInput").value.trim();
const loader=document.getElementById("loader");
const vSec=document.getElementById("validSection");
const iSec=document.getElementById("invalidSection");
const vList=document.getElementById("validList");
const iList=document.getElementById("invalidList");
if(!input){alert("请输入内容");return}
loader.style.display="block";vSec.style.display="none";iSec.style.display="none";vList.innerHTML="";iList.innerHTML="";
try{
const res=await fetch('/ip='+encodeURIComponent(input));
const data=await res.json();
const results=Array.isArray(data)?data:[data];
let hasV=false,hasI=false;
results.forEach(item=>{
let h='';
const ok=item["状态"]&&item["状态"].includes("有效");
const cls=ok?"valid":"invalid";
const sCls=ok?"status-text-ok":"status-text-fail";
h+=`<div class="result-card ${cls}">`;
h+=item["错误"]?`<div class="result-row"><span class="label">状态:</span><span class="val ${sCls}">${item["错误"]}</span></div>`:`<div class="result-row"><span class="label">状态:</span><span class="val ${sCls}">${item["状态"]}</span></div>`;
h+=`<div class="result-row"><span class="label">地址:</span><span class="val">${item["地址"]}</span></div>`;
if(item["地区"])h+=`<div class="result-row"><span class="label">地区:</span><span class="val">${item["地区"]}</span></div>`;
h+=`</div>`;
if(ok){vList.innerHTML+=h;hasV=true}else{iList.innerHTML+=h;hasI=true}
});
loader.style.display="none";if(hasV)vSec.style.display="block";if(hasI)iSec.style.display="block";
}catch(e){loader.style.display="none";iSec.style.display="block";iList.innerHTML=`<div class="result-card invalid">请求失败，请检查网络连接</div>`}
}
</script>
</body>
</html>"""

@app.get("/ip={user_input:path}")
async def check_proxy_ip_path(request: Request, user_input: str):
    results = await resolve_and_check(user_input)
    return JSONResponse(content=results)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
