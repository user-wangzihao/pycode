# 阶段四 · feedparser 新闻采集站 总结

> 归档用。承接「阶段四(采集层)交接总结」第五节"下一站:feedparser"。
> 本站完成:从结构化股价 → 非结构化新闻流的质变,打通 feedparser 数据结构、网络/解析分层、源列表底盘、两层容错。唯一未碰的脏:简体中文编码(下一局)。
> 标的:小米港股 `1810.HK`(已定)。脚本目录:`D:\pycode\day12\`(feedparser-01/02/03.py)。

---

## 一、本站走过的三级跳

| 脚本 | 干了什么 | 核心收获 |
|---|---|---|
| feedparser-01 | `feedparser.parse(url)` 让库自己抓,打印四件套 | 看清数据结构 + bozo 哨兵 + 字段映射野怪 |
| feedparser-02 | requests 抓字节 → `feedparser.parse(bytes)` | 网络层/解析层切开;`resp.content` 编码预防针;复用 `with_retry` |
| feedparser-03 | 源列表 + 循环 + 两层容错 + provenance | 单源→多源底盘;跨源重复坐实;故障注入验两层容错 |

**质变点**:之前 akshare 给的是结构化表格(行列整齐),feedparser 给的是非结构化新闻流——**这才是 LLM 抽取层真正要读、要提买卖信号的料**,整条 Agent 流水线在此首尾呼应。

---

## 二、feedparser 数据结构(API 实测)

**Java 类比**:feedparser ≈ 超宽容的 Jackson/JAXB。各种方言(RSS 0.9/1.0/2.0、Atom)喂进去都反序列化成同一对象模型,字段名归一。

返回对象关键属性:
- `d.bozo` —— 0/1 哨兵,解析是否有瑕疵
- `d.bozo_exception` —— bozo=1 时的具体异常,判严重程度
- `d.status` —— HTTP 状态码(`parse(url)` 自抓时才有;喂 bytes 时为 None)
- `d.feed` —— 频道级元数据(`d.feed.title` 等)
- `d.entries` —— 新闻条目列表(本站每源稳定 20 条)

**字段映射野怪(同 akshare "开/收/高/低"反直觉同类)**:RSS 原文标签 feedparser 会改名——
- `<description>` → `entry.summary`
- `<pubDate>` → `entry.published`(字符串)**并附赠** `entry.published_parsed`(`time.struct_time`)

**纪律**:逐 entry 用 `e.get("title")` 而非 `e.title`。缺字段时 `.get` 返回 None,`e.title` 抛 AttributeError(对应"字段可能缺失"野怪)。

---

## 三、★ bozo —— "HTTP 200 ≠ 业务成功"的新马甲(silent failure again)

feedparser.parse() **几乎不抛异常**。feed 坏了、网断了、404 了,都默默返回对象,只把错误塞进 `.bozo` / `.bozo_exception`。这是阶段三 silent failure 老朋友。

**自守三件套**:不能只看"跑没跑通",必须查 `.bozo` + `.status` + `len(.entries)`。
- 本站 Yahoo 源全程 `bozo=False`、`status=200`、entries=20,过得很干净。
- 预告的"summary 混 HTML 标签"这只怪**本站没出现**(Yahoo summary 是纯文本繁中)——预告是假设,核对是真相。HTML 那只怪会在别的源(新浪/东财正文)出现。

---

## 四、★★ 早绑定 vs 晚绑定:为什么 feedparser 没重演"代理仗"

同样是"第三方库自己抓取",akshare 当初代理被焊死、feedparser 这次乖乖走代理,根因在**绑定时机**:

- **akshare = 早绑定**:`import` 那一刻就 new 了一个 `requests.Session`,proxies 固化进去。之后改环境变量,它那个 Session 不回头看。(`proxy_debug.py` 实测 akshare Session.proxies={})
- **feedparser = 晚绑定**:用 `urllib`,每次 `parse()` 内部才 `build_opener()`,默认塞的 `ProxyHandler` 在**调用那一刻现读 `getproxies()`(即环境变量)**。net.py 在 import 时设的 `HTTP_PROXY`,等到 parse 那刻被现场读到 → 生效。

**一句话**:akshare import 时固化代理(早绑定),feedparser 调用时现读代理(晚绑定)。
**Java 类比**:早绑定 = Spring bean 启动时 `@Value` 注入完,之后 `System.setProperty` 它不认。

**但"晚绑定碰巧能用" ≠ 架构可控**:`feedparser.parse(url)` 在库内部抓,① `with_retry` 套不进去;② 状态码/超时/UA 插不上手;③ 万一站点对默认 UA 返 403 束手无策。→ 这正是 feedparser-02 要把网络层切出来的理由。

---

## 五、★ 网络层 / 解析层切开(net_check.py 方法论的延续)

```python
@net.with_retry()                      # 网络层:复用重试(退避+异常筛子+日志)
def fetch_feed_bytes(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()            # 非 2xx 抛 HTTPError ⊂ RequestException → 落进筛子重试
    return resp.content                # ★ 字节,不是 text
raw = fetch_feed_bytes(URL)
d = feedparser.parse(raw)              # 纯解析,只干一件事
```

**唯一新认知点,盯死一行 `return resp.content`(字节)而非 `resp.text`(字符串)**:
- feed 的编码声明写在 XML 头 `<?xml encoding=...?>`。
- 给 `resp.text` → requests **已先用它自己猜的编码**解码,中文常猜错 → 乱码。
- 给 `resp.content`(原始字节)→ 让 feedparser 用它**自带的、看得懂 feed 编码声明**的检测去解。
- **这就是简体中文源那场编码仗的预防针**:网络库别替 feedparser 做编码决定。

`HEADERS` 伪装浏览器 UA,绕站点对脚本默认 UA 的拦截。

**小坑(记钩子不展开)**:`raise_for_status` 对 404 等 4xx 也会触发重试,但 4xx 重试无意义,是个可优化点。按 ROI 先不过度设计。

---

## 六、★ 空数据自守该放哪一层 —— 看数据语义,不抄模板

feedparser-02 的 `if not d.entries: raise` 写在**重试圈外**;akshare 当初 `if data.empty: raise` 写在**重试圈内**。同样是"空数据自守",位置相反。**反转:这次圈外可能反而对**——

- **股价(akshare)**:某只股票永远有历史价,返回空 ≈ 服务端抽风 → **该重试**(放圈内)。
- **新闻(feed)**:冷门标的**可能真的近期没新闻**,空是合法业务状态 → 重试 5 次还是空,白等 30 秒 → **该快速失败**(放圈外)。

**铁律**:"空数据要不要进重试圈"不是抄模板,是看数据语义。要知道自己为什么这么放,而不是碰巧放对。这是 silent failure 自守的进阶版——连"自守放哪一层"都要想清。

---

## 七、★★ 源列表底盘 + 两层容错(feedparser-03)

```
SOURCES = [{name, url}, ...]            # 抽 feed 源列表
for src in SOURCES:
    try:
        items = parse_one_source(src)   # 抓+解析+给每条挂 source(provenance)
        if not items: ... continue      # 空源跳过
        all_news.extend(items)
    except Exception as ex:             # ★ 宽抓:单源任何爆炸只埋这一个,for 继续
        print(f"✗ {src['name']} 跳过 → {type(ex).__name__}: {ex}")
```

### 两层容错,判决相反,因为目标相反
| | 重试圈(with_retry 异常筛子) | 批处理圈(for 的 except Exception) |
|---|---|---|
| 抓法 | **窄抓** | **宽抓** |
| 目标 | 别把 bug 当网络抖动重试 | 别让一个源杀死整批 |
| KeyError | 立刻炸 | 也接住,但 `type(ex).__name__` 让它日志现形 |

**关键护身符**:那句 `type(ex).__name__: ex` —— 就算真有 bug,也会在日志里现形,**宽抓 + 记类型 ≠ 吞异常**。
**Java 类比**:Spring Batch fault-tolerant step,skip 坏记录 + 记 skip 数,而非整 job 回滚。
**姿势切换**:开发期想看完整 traceback 定位 bug,临时注释掉这个 except 裸跑;生产期才需要它兜底。

### provenance(来源标记)是为下游埋的桩
每条带 `source`,眼下没用,但**去重(hash + pymilvus)、知识图谱匹配、评分融合**都要知道"这条几个源都报了"(多源印证=强信号)。先采全、先标来源,精筛在后。

---

## 八、★ 跨源重复坐实 → 两套去重的动机(实测撞出来)

3 源 × 20 条 = **60 条 → 唯一 link 仅 45**,差 15 条重复。
- 同一篇《全日速報》《港股半日》大盘横扫稿,`link` **字节级相同**,同时挂在小米/阿里/腾讯三只 feed 下。
- → **这 15 条就是阶段七 hash 去重那一半的活教材**(link 一撞就掉)。
- → "不同媒体报同一事件、link 不同但正文相似"那一半,才需要 **pymilvus 向量去重**。
- **两套去重的动机,这一跑亲眼撞出来了。**

---

## 九、★ 故障注入(改坏域名 feedsqqw)撞出的三个真发现

退避链 `2→2→4→8` 全打出、`SSLError`⊂`RequestException` 被筛子接住重试、耗尽抛 `RetryError` 被外层 except 跳过、其余两源照常出数(40 条)——**两层容错串起来全验到**。顺带:

1. **`UNEXPECTED_EOF_WHILE_READING` 同形不同因**:这报错"代理仗"第 3 条见过(台湾 5x 节点掐大包),但**这次根因是域名不存在/代理连不上目标**导致 SSL 握手 EOF。**同一报错形态、两个根因** → 复习铁律:报错按"卡在哪一层"读,别照错误文本对号入座。
2. **`RetryError` 套娃真异常**:tenacity 重试耗尽抛的是 `RetryError`,原始 `SSLError` 被裹在里面。下游想精确分类(SSL 错 vs 超时错)`except SSLError` 抓不到,需 `ex.last_attempt.exception()` 剥出里层。(Java 类比:`ExecutionException`/`UndeclaredThrowableException` 套真异常,要 `getCause()`。)钩子记下。
3. **30 秒串行拖累**:单死源 2+2+4+8=16s 退避 + 连接超时,实测十几秒。**源一多,死源退避串行累加拖死整批**。优化方向(记钩子,先不做):重试次数/封顶按源健康度调小、或多源并发抓(死源各等各的)。

---

## 十、★ 数据质量真信号(面试硬货)

前 3 条标题全是《全日速報》《港股》《半日速報》港股大盘速报,只"顺带提一句小米跌 3%",**不是小米专题新闻**。
→ **按股票代码订阅 ≠ 拿到的都是该股专属新闻**。相关性过滤/降噪是下游的活(LLM 抽取判定 + 评分融合)。
→ **采集层先采全,后降噪**,跟"新闻来源广泛 = 架构抽 feed 源列表、汇总去重"一脉相承。先求全,精筛在后。

---

## 十一、待办 / 钩子(别忘)

- [ ] **下一局:简体中文源编码仗**(新浪/东财/RSSHub)——`resp.content` 预防针的实战考场。预计撞:HTTP 头与 XML 声明编码标注矛盾、GBK/GB2312、bozo 可能终于变 1。
- [ ] `published_parsed` 是 `struct_time`,**不可 JSON 序列化** → 阶段五/存储前必须转 datetime 或字符串,否则一存就炸。
- [ ] `published_parsed` 是 **UTC 归一化**值;若源给 `+0800`,parsed 会被转成 UTC(减 8h),别当本地时间用(阶段五日期处理)。
- [ ] 全文 ≠ summary:Yahoo summary 是**截断预览**(三条结尾都断在半句),要全文得顺 `link` 抓网页正文 → **这才是 BeautifulSoup 真正的用武之地**(抓正文),不是清洗 summary 标签。
- [ ] `RetryError` 剥里层异常(`last_attempt.exception()`)——下游若需精确分类再做。
- [ ] 死源 30s 串行拖累 → 重试调参 / 并发抓(优化项,非阻塞)。
- [ ] 4xx 不该重试(`raise_for_status` 触发了无意义重试)——可优化。

---

## 十二、环境备忘(不变,延续上一份交接)

- 采集层出网:Clash 全局 + 香港原生 IP 节点,`net.py` 在 import 网络库**之前**设 `HTTP_PROXY/HTTPS_PROXY=http://127.0.0.1:7897`(**走代理**,与阶段三 DeepSeek `trust_env=False` 直连相反)。
- `import net` 必须第一行(地基,import 即生效)。
- 已装:akshare、pandas、lxml、beautifulsoup4、tenacity、**feedparser**、requests。
- 标的:小米港股 `1810.HK`(港股价接口将来用 `stock_hk_hist`,非 A 股 `stock_zh_a_hist`)。
