"""Local microwave-matching knowledge base used by the agent and MCP clients."""

from __future__ import annotations

import re
from typing import Any, Dict, List

SECTIONS: List[Dict[str, Any]] = [
    {
        "id": "smith-basics",
        "title": "史密斯圆图基础",
        "keywords": ["史密斯", "smith", "反射系数", "gamma", "归一化", "圆心"],
        "text": (
            "史密斯圆图把归一化阻抗 z=Z/Z0 映射到反射系数 Γ=(z-1)/(z+1)。"
            "圆图中心 Γ=0 对应 Z=Z0（通常 50Ω）；外圆 |Γ|=1 对应纯电抗。"
            "等电阻圆与实轴相切于 (1,0)，等电抗圆也经过 (1,0)。"
            "匹配的目标就是把阻抗点移动到圆心，此时 |Γ|=0、VSWR=1、回波损耗为无穷大。"
        ),
    },
    {
        "id": "series-shunt",
        "title": "串联与并联元件的圆图轨迹",
        "keywords": ["串联", "并联", "轨迹", "等电阻圆", "等电导圆", "电感", "电容"],
        "text": (
            "串联元件改变电抗：Z→Z+jX，阻抗点沿等电阻圆移动；串联电感向上（+jX），"
            "串联电容向下（−jX）。并联元件改变电纳：Y→Y+jB，阻抗点沿等电导圆移动；"
            "并联电容使电纳增加（+jB），并联电感使电纳减少。"
            "记忆口诀：串阻并导，串感上串容下，并容上并感下。"
        ),
    },
    {
        "id": "l-network",
        "title": "L型网络的选择与设计",
        "keywords": ["l型", "l网络", "低阻", "高阻", "q值", "两元件"],
        "text": (
            "L型网络只有两个自由元件，Q 值由阻抗变换比唯一决定：Q=√(R_high/R_low−1)。"
            "当 R_L<Z0 时使用 L型（右）：源端并联 C1，再串联 L+C2，"
            "C1=Q/(Z0ω)，C2=1/[ω(ωL+X_L−Q·R_L)]。"
            "当 R_L>Z0 时使用 L型（左）：先并联 C1 把等效电阻降到 Z0，再串联 L+C2。"
            "L型网络效率高、元件少，但带宽由 Q 固定，不能独立选择。"
        ),
    },
    {
        "id": "t-network",
        "title": "T型网络",
        "keywords": ["t型", "t网络", "三元件", "虚拟电阻", "串联c3", "并联lc"],
        "text": (
            "T型网络为 源—串联 C3—节点（并联 L+C2 到地）—串联 C1—负载。"
            "C3 先把 50Ω 变换成一个中间虚拟电阻 R_virtual=1/Re{Y_left}，"
            "负载经 C1 串联变换后在同一节点呈现相同电导，最后由 L+C2 谐振抵消电纳。"
            "三元件多出的自由度可用于选择带宽或元件值，但 C3 过大会使 R_virtual 降到 50Ω 附近，"
            "从而无法匹配高阻负载；C3 过小则需要很小的 C2。"
        ),
    },
    {
        "id": "pi-network",
        "title": "π型网络Ⅰ与Ⅱ",
        "keywords": ["π型", "pi型", "pi1", "pi2", "c-l-c", "三元件"],
        "text": (
            "π型Ⅰ：源—并联 C3—串联 L+C2—并联 C1—负载。C3 决定源端等效串联电阻，"
            "C1 完成负载端电阻变换，L+C2 抵消电抗。"
            "π型Ⅱ：源—并联 C1—串联 L+C2—并联 C3—负载。C3 先对负载做导纳变换，"
            "C1 再用 Q=√(Z0/R_eff−1) 完成 50Ω 侧变换。"
            "π型网络的两个并联电容使设计自由度更高，适合低阻或需要调节带宽的场合，"
            "但元件多、损耗与寄生更敏感。"
        ),
    },
    {
        "id": "q-bandwidth",
        "title": "Q 值与带宽",
        "keywords": ["q值", "带宽", "vswr", "窄带", "宽带", "bw"],
        "text": (
            "匹配网络的 Q 值越高，阻抗轨迹越靠近圆图外缘，带宽越窄。"
            "单节 L 型网络的 Q 由 R_high/R_low 决定，分数带宽近似 BW≈1/Q（VSWR<2 时更宽）。"
            "三元件 T/π 网络可以通过选择中间虚拟电阻来降低 Q、展宽带宽，"
            "但会牺牲元件数量和效率。若带宽仍不足，应采用多节匹配或微带/分布式结构。"
        ),
    },
    {
        "id": "component-reality",
        "title": "实际元件的寄生与自谐振",
        "keywords": ["寄生", "自谐振", "srf", "q值元件", "封装", "0402", "0603"],
        "text": (
            "实际贴片电容有 ESL，电感有 EPC。电容在自谐振频率 SRF 以上呈感性，"
            "电感在 SRF 以上呈容性，因此设计值必须低于 SRF 并留有余量。"
            "0402 电容的 SRF 通常高于 0603；高 Q 射频电容（如 NP0/C0G）优于 X7R。"
            "当计算出的 C 小于 0.1pF 或 L 小于 1nH 时，PCB 走线寄生会主导结果，"
            "应降低固定电感值、提高频率或改用分布式匹配。"
        ),
    },
    {
        "id": "voltage-stress",
        "title": "元件耐压与功率承受",
        "keywords": ["耐压", "电压", "电流", "功率", "击穿", "rms", "峰值"],
        "text": (
            "匹配网络在失配或高功率下会出现远高于源电压的节点电压。"
            "对于 50Ω 系统、输入功率 P，匹配时输入峰值电压约为 √(2P·50)=10√P。"
            "高 Q 节点电压会被 Q 倍放大；容性/感性负载在谐振点附近也可能产生高压。"
            "工程选型应同时检查峰值电压、RMS 电流、额定功率降额（通常 50%）和温度。"
            "本软件的耐压模块用完整网络节点法求解，包含源阻抗的负载效应。"
        ),
    },
    {
        "id": "range-scan",
        "title": "匹配范围扫描",
        "keywords": ["匹配范围", "正向", "扫描", "覆盖", "grid", "可匹配"],
        "text": (
            "正向扫描固定拓扑与固定元件（如 L、C3），遍历可调电容范围，"
            "计算终端能覆盖的负载阻抗集合。扫描点越多，边界越精确，但计算量按维度增长。"
            "三元件网络需要三维扫描，软件默认限制网格规模以保证交互流畅。"
            "若目标负载落在扫描区域之外，应更换拓扑、调整固定元件或增加可调范围。"
        ),
    },
    {
        "id": "vswr-conversion",
        "title": "VSWR、回波损耗与 |S11| 换算",
        "keywords": ["vswr", "驻波", "回波损耗", "s11", "db", "反射"],
        "text": (
            "|Γ|=(VSWR−1)/(VSWR+1)；VSWR=(1+|Γ|)/(1−|Γ|)。"
            "回波损耗 RL=−20log10|Γ| dB；|S11|dB=20log10|Γ|。"
            "VSWR=1.5 对应 |Γ|=0.2、RL≈14dB；VSWR=2 对应 |Γ|=1/3、RL≈9.54dB。"
            "工程上常用 VSWR<2（RL>9.5dB）作为合格线，要求更高时用 VSWR<1.5。"
        ),
    },
    {
        "id": "topology-selection",
        "title": "五种拓扑如何选",
        "keywords": ["选择", "拓扑", "对比", "推荐", "自动"],
        "text": (
            "① 负载 R<50Ω 且以实部为主：优先 L型（右），元件最少、效率最高。"
            "② 负载 R>50Ω：优先 L型（左）。"
            "③ 需要更宽带宽或 L 型无解：T型或 π型。"
            "④ 低阻负载且希望源端/负载端都可调：π型Ⅱ。"
            "⑤ 高阻或需要中间节点调节：T型。"
            "强容性负载（X 很负）会让固定电容拓扑的 C1/C2 无正解，此时优先 L型（右）"
            "或改用串联电感方案。软件提供 auto 模式自动比较五种拓扑。"
        ),
    },
    {
        "id": "design-workflow",
        "title": "推荐设计流程",
        "keywords": ["流程", "步骤", "工程", "验证", "报告"],
        "text": (
            "1) 明确频率、带宽、功率与负载阻抗（含容差）。"
            "2) 用 auto 或 L 型得到初始解；检查 VSWR、S11 与元件值是否可实现。"
            "3) 查看带宽与 ±5% 灵敏度；必要时换三元件拓扑降低 Q。"
            "4) 用实际元件模型（寄生、SRF、Q）复核；预留调试裕量。"
            "5) 做耐压/电流校核，选择额定值至少 2 倍余量的器件。"
            "6) 导出报告并在 Smith 圆图上核对轨迹。"
        ),
    },
    {
        "id": "worked-example",
        "title": "例题：2.4GHz、20+j5Ω 的匹配",
        "keywords": ["例题", "2.4ghz", "2400", "20+j5", "示例"],
        "text": (
            "在 2.4GHz 匹配 20+j5Ω 到 50Ω。R_L<50Ω，先试 L型（右）。"
            "Q=√(50/20−1)=1.2247；C1=Q/(50ω)=1.62pF（ω=2π·2.4GHz）。"
            "选择 L≈1.94nH，则 C2≈6.80pF。节点法复核 Zin=50.00+j0.00Ω、VSWR=1.0000。"
            "该设计在 VSWR<2 下的分数带宽约 57%。若带宽不足，可改用 T 型（约 72%）。"
        ),
    },
    {
        "id": "mcp-usage",
        "title": "通过 MCP 调用本软件",
        "keywords": ["mcp", "zcode", "智能体", "工具", "api"],
        "text": (
            "本软件提供 stdio MCP 服务，工具包括 design_matching_network、"
            "scan_matching_range、evaluate_network、compute_voltage_stress、"
            "analyze_bandwidth、compare_topologies、search_knowledge、export_design_report 等。"
            "在 ZCode 的 MCP 配置中加入命令 python app/run_mcp.py 即可。"
            "智能体应先调用工具获取数值，再解释公式；不要凭空编造元件值。"
        ),
    },
    {
        "id": "matching-limit",
        "title": "为什么有些负载无法用固定电容网络匹配",
        "keywords": ["无解", "匹配不了", "负电容", "限制", "强容性"],
        "text": (
            "本软件的 T/π 拓扑只使用串联电容和并联电容，元件电抗符号固定。"
            "强容性负载（X_L 很负）需要串联电感来抵消，若拓扑中没有串联电感，"
            "就会求出负的 C1/C2，物理上不可实现。"
            "强感性负载（B_L 很负）需要并联电感，若只有并联电容也会无解。"
            "此时应更换拓扑（例如低阻强容性用 L型右）或引入电感型匹配网络。"
        ),
    },
]

_STOP = set("的了吗呢是在和与或及我对你他她它这那为把被从到用如何怎么什么一个可以需要能够以及进行实现一下请问".split())


def _tokens(query: str) -> List[str]:
    q = (query or "").lower()
    words = re.findall(r"[a-z0-9\.\+\-]+|[\u4e00-\u9fff]{2,}", q)
    out = []
    for w in words:
        if w in _STOP:
            continue
        out.append(w)
        if len(w) > 3 and re.fullmatch(r"[\u4e00-\u9fff]+", w):
            out.extend(w[i:i + 2] for i in range(len(w) - 1))
    return list(dict.fromkeys(out))


def search(query: str, limit: int = 4) -> Dict[str, Any]:
    toks = _tokens(query)
    scored = []
    for s in SECTIONS:
        hay = (s["title"] + " " + s["text"] + " " + " ".join(s["keywords"])).lower()
        score = 0.0
        for t in toks:
            if t in s["keywords"]:
                score += 4.0
            elif t in s["title"].lower():
                score += 3.0
            elif t in hay:
                score += 1.0
        if score > 0:
            scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        scored = [(0.0, s) for s in SECTIONS[:3]]
    return {
        "ok": True,
        "query": query,
        "results": [
            {"id": s["id"], "title": s["title"], "text": s["text"], "score": sc}
            for sc, s in scored[: max(1, min(limit, 8))]
        ],
    }


def all_sections() -> List[Dict[str, Any]]:
    return SECTIONS
