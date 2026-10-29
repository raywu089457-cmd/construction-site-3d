# 工地 3D 場景 · 組裝編輯器

用 three.js 做的四個網頁：展示、比較、場景、以及一個可以自由擺放零件、
分階段組裝、最後匯出一部「工進動畫」MP4 的編輯器。

全部素材都是 CC0 或 CC-BY；伺服器只用到 Python 標準庫 + ffmpeg。

## 快速開始

```bash
python serve.py --port 4211
# 開 http://127.0.0.1:4211/
```

`serve.py` 除了當靜態伺服器，還提供匯出 API（見下面「工進動畫」）。

`/` 會自動跳到 **`editor.html`**，編輯器是整個工作台的入口：上方一排導覽按鈕可以切到
其他頁面，其中「建材貼圖」「結構建材」是**內嵌**（不離開編輯器，按 × 或 Esc 關閉）。

| 頁面 | 內容 |
|---|---|
| `editor.html` | **入口 + 組裝編輯器**（42 種零件、鎖點、階段、運鏡、匯出 MP4） |
| `gallery.html` | 9 個 SimReady 圍籬（寫實高模，已減面成網頁可用） |
| `free.html` | OpenGameArt CC0 工地包 + 挖土機/堆高機 |
| `scene.html` | 兩邊素材合體的完整工地場景，三種預設視角 |
| `materials.html` | 9 組建材 PBR 貼圖展示（磚、混凝土、膠合板、碎石、鏽蝕、瀝青、砂） |
| `structure.html` | **程序化結構建材生成器**：混凝土／模板／鋼筋／鷹架／組合，全部可調參數 |

## 編輯器怎麼用

```
左側零件庫 34 種 → 點一下出現在鏡頭前
拖曳移動 · R 旋轉 · Del 刪除 · 靠近鎖點會自動吸附
右側設定階段（1..6）與機位（調好角度按數字捕捉）
底部時間軸拖曳可前後預覽
▶ 播放  ⬇ 匯出 MP4  存檔 JSON / 讀檔
```

### 鎖點系統

不手寫座標，從 bbox 自動推導：

```
ground  (0, 0, 0)            所有零件都有
endL/R  (±半長, 0.55h)       細長型（長邊可能在 X 也可能在 Z）
top     (0, h, 0)            矮的 / 可堆疊
配對規則：endL↔endR、ground↔top
吸附半徑：2.2 m
```

實測：兩片 6 m 圍籬接起來間距 6.03 m（正好一個 panel），木箱疊上去 0.47 m（正好箱高）。

### 工進動畫

整段動畫是 `t` 的**純函數**：

```js
renderAt(t) {
  階段 s   = floor(t / 1.0) + 1
  出現 u   = easeOut((t - (s-1)) / 0.55)
  零件      scale = u,  y = 0.6 × (1 - u)   // 從上方落下
  鏡頭      在關鍵影格之間用 smoothstep 插值
}
```

所以拖時間軸可以任意跳、匯出的影片每次完全一樣。

匯出不是用 `MediaRecorder` 即時錄影（掉幀就毀），而是**逐格算圖交給 ffmpeg**：

```
瀏覽器 renderAt(t) → canvas.toBlob(jpeg) → POST /_export/frame?i=N
                                          → _frames/f00042.jpg
POST /_export/finish?fps=30               → ffmpeg libx264 → MP4
```

實測 90 格（3 階段 × 1 秒 × 30 fps）：算圖 1.0 s、編碼 0.8 s、輸出 1.2 MB。

## 素材來源與授權

| 來源 | 授權 | 用在哪 |
|---|---|---|
| **NVIDIA SimReady Assets** (`nvidia/simready-assets`) | **CC BY 4.0**（每個資產內有 `.metadata/LICENSE.txt`） | 圍籬、拒馬、木箱、桶子、手工具… |
| **OpenGameArt**「3D House Construction Site」by Majadroid | **CC0** | 施工大樓、塔吊、工程車、貨櫃、地面 |
| **OpenGameArt** excavator / forklift | **CC0** / CC-BY | 挖土機、堆高機 |
| **Poly Haven** 模型 | **CC0** | 水泥袋、混凝土護欄、木梯/伸縮梯、鋼管×2、塑膠箱×3、木箱×2、木桶、鐵桶、瓦斯桶、石塊、碎石堆 |
| **Poly Haven** 貼圖 | **CC0** | 9 組 PBR：紅磚、空心磚、清水混凝土、膠合板、碎石、鏽蝕鋼板、鏽蝕浪板、瀝青、砂土 |

CC BY 的素材需要標註作者，使用時請保留上表。

### SimReady 素材怎麼變成網頁可用的

原始資產是給 Omniverse / Isaac Sim 做物理模擬的，精度是「螺栓都要做出來」的等級
（例如 `environment_fence_b01` 原始有 **292 萬個三角形、2.3 GB**）。

處理流程（見 `usd2glb_lite.py`）：

1. `prep_lite.py`：複製 USD 結構，把 4K UDIM 貼圖縮到 512–1024 px
   （Blender 的 `img.scale()` 對 UDIM 無效，所以先縮圖再匯入）
2. `usd2glb_lite.py`：Decimate 減面並 **apply**，然後匯出 GLB
3. 網頁端再依 geometry UUID 去重（Blender 會把 prototype 和實體各寫一個 node）

結果：2.9 GB 的圍籬 → 9.3 MB / 5 萬面。

## 程序化結構建材（structure.html）

結構體建材是重複性幾何，用程式生成比找模型準確：

| 構件 | 內容 | 參數 |
|---|---|---|
| **混凝土** | 柱 / 樑 / 板 / 牆 | 寬、深、高、長、厚 |
| **模板** | 18 mm 膠合板 + 橫檔 + 對拉螺栓 | 柱寬深高、模板間隙 |
| **鋼筋** | 柱（4 主筋 + 箍筋）/ 板（雙層雙向鋼筋網） | 鋼筋徑、間距、保護層 |
| **鷹架** | φ48 立桿、橫桿、斜撐、踏板、底座 | 跨距、層高、層數、排數、跨數 |
| **組合** | 鋼筋 → 混凝土 → 模板 → 鷹架（施工順序並列） | 柱高、鷹架層數 |

貼圖直接吃 `textures/` 裡的 PBR：混凝土用 `brushed_concrete`、模板用 `plywood`、鋼筋與鷹架用 `rusty_metal`。

## BIM / Revit 素材說明

`.rfa`（Revit 家族）**沒有免費的轉檔路徑**：ProtoTech / CAD Exchanger / datakit 的
RFA→glTF 轉換器全部需要先安裝 Revit，convert.guru 是線上付費服務。
Blender 5.2 也不內建 IFC / DXF 匯入（需要另外裝 Bonsai 或 DXF addon）。

能直接吃進這個專案的格式：**glTF/GLB、FBX、OBJ、USD/USDa、.blend**。
所以素材都從提供這些格式的來源取得（Poly Haven、OpenGameArt、Quaternius、Kenney）。

**IFC 可以轉**（`tools/ifc2glb.py`，用 ifcopenshell + trimesh）：

```bash
pip install ifcopenshell trimesh scipy numpy
python tools/ifc2glb.py model.ifc out.glb
```

實測 buildingSMART 官方 `Building-Structural.ifc`：16 個構件、1,496 面、40 KB。
BIM 模型只有材質名稱沒有貼圖，所以轉出來是平塗色（依名稱對應混凝土／鋼構／木作／磚）。

免費 IFC 來源：buildingSMART Certification-datasets、BIMobject、BIM&CO、Modlar。

## 已知限制

- 編輯器是為滑鼠設計的，手機只能瀏覽不能編輯
- 每階段固定 1 秒，尚不能自訂
- 零件出現動畫只有「落下 + 縮放」
- 影片解析度跟隨視窗大小

## 檔案

```
serve.py           靜態伺服器 + 匯出 API
editor.html        組裝編輯器
scene.html         合體工地場景
index.html         9 個 SimReady 圍籬
free.html          免費包機具
vendor/            three.js r169（本地，不依賴 CDN）
models/            轉好的 GLB
```
