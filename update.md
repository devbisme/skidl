# 更新记录（human_readable 布局 / 走线稳定化）

**日期**：2026-05-13  
**范围**：原理图自动布局与走线（`place.py`、`route.py`），默认行为不变。

---

## 目的

- 在可选模式下让生成的 `.kicad_sch` 更接近工程师手工排版习惯（主控居中、电源/去耦分区、接口左右等启发式）。
- 减少随机性，使同一输入多次生成坐标与走线更稳定。
- 遵循小步、保守、可回滚：不引入新依赖、不重写整个 placer/router。

---

## 涉及文件

| 文件 | 说明 |
|------|------|
| `src/skidl/schematics/place.py` | 主要改动：`human_readable` 分支、工具函数、auto_stub 微调、默认 seed |
| `src/skidl/schematics/route.py` | 轻量改动：稳定 `global_router` 起点、`remove_jogs` 顺序、`humanize_wires`、默认 seed |

---

## 如何启用

在调用 `place` / `route` 时传入可选参数：

```python
node.place(..., human_readable=True)
node.route(..., human_readable=True)
```

- **`human_readable=False`（默认）**：保持原有逻辑与分支，与改动前一致。
- **`human_readable=True` 且未传 `seed`**：内部使用固定默认种子 `0`，便于回归与对比输出。

---

## `place.py` 变更摘要

### 新增（`Placer` 内小工具，非新 public API）

- `_part_ref_key(part)`：按 `ref` / `name` / `value` 稳定排序键。
- `_net_names_of(part)`：安全返回器件所连 net 名称集合。
- `_is_power_net_name(name)`：电源/地 net 名启发式。
- `_classify_part_role(part)`：`power` / `decoupling` / `ic` / `connector` / `passive` / `other`。
- `_find_main_part(parts)`：优先 pin 数最多的 IC，否则连接度最高，tie 用稳定排序。
- `_place_row(...)`：按 `place_bbox` 与 `GRID` / `BLK_INT_PAD` 行摆放。

### `place_connected_parts_rowbased`

- **`human_readable=True`**：按主器件 + 角色分区布局；末尾保守去重叠 + `snap_to_grid`。
- **`human_readable=False`**：仍为原 BFS + 行打包逻辑。

### `place_floating_parts`

- **`human_readable=True`**：按 role 分桶、`value/ref` 稳定排序，被动件按 R/C/L 等分行，不依赖随机初始布局。
- 默认路径不变（含大数量浮动件 + `auto_stub` 的 sqrt grid 等）。

### `place_blocks`

- 当 block 数量超过阈值且 **`human_readable=True`**：连通块居中行、浮动块下方、子 sheet 右侧，按 `tag`、面积、`ref` 稳定排序。
- 默认仍为原 sqrt grid + 力导向等。

### `_auto_stub_large_groups`

- **`human_readable=True` 且 `auto_stub=True`**：更倾向对电源类 net 与候选链 net 排序后做有限次数 stub，避免“全图标签化”；默认分支保持原等步长切割逻辑。

### `place()` 随机种子

- `human_readable=True` 且用户未传 `seed` 时，使用固定种子 `0`。

---

## `route.py` 变更摘要

### `route()`

- 与 place 一致：`human_readable=True` 且无 `seed` 时默认 `seed=0`。
- 将本次 `options` 暂存于 `node._route_options`，供内部读取；正常结束或 `RoutingFailure` 时清理。

### `global_router()`

- **`human_readable=True`**：`start_face` 按 track 坐标、beg/end、pin/terminal 数量等可比较键排序后取第一个，替代 `random.choice`。
- 默认仍为随机选择。

### `cleanup_wires()` 内 `remove_jogs()`

- **`human_readable=True`**：不对 segments / `p2s` 做 `shuffle`.改为稳定排序顺序。
- **`human_readable=True`**：在通用 `cleanup_wires` 流程末尾调用 `humanize_wires()`。

### `humanize_wires()`（新增）

- 仅在 human 模式、且 `cleanup_wires` 之后执行。
- 保守操作：去零长段、稳定排序、对极短且弱连接的 stub 做 trim；不改动电气连接语义；避免穿越器件 bbox 的激进简化未做。

---

## 验收与自检

- `python -m compileall src/skidl/schematics/place.py src/skidl/schematics/route.py` 通过。
- `import skidl.schematics.place`、`import skidl.schematics.route` 通过（环境缺 KiCad 符号路径时可能有既有 WARNING，与本次改动无关）。

---

## 回滚说明

- 不传 `human_readable` 或显式 `human_readable=False` 即可恢复改动前行为。
- 若需完全撤销代码：仅回退上述两个文件在本记录日期附近的提交即可。

---

## 2026-05-14 更新：human 路由崩溃修复 + 网表仓库默认输出目录

### 1. `route.py` — `SwitchBox.coalesce` KeyError

- **现象**：`human_readable=True` 时，部分电路在 `create_switchboxes` → `coalesce` 中执行 `(box_face.switchboxes - {box}).pop()` 会因邻接集为空触发 **`KeyError: 'pop from an empty set'`**（例如 `examples/5micro_3`）。
- **原因**：布局/track 切分退化时，某 face 上记录的 `switchboxes` 可能未包含预期邻盒，空集仍被 `pop()`。
- **修复**：先判断 `adjacent = box_face.switchboxes - {box}` 非空再取邻盒；扩张循环内先收集 `(i, adj_box)`，若任一步邻接为空则放弃该生长方向并 `continue` 下一轮，避免部分替换与崩溃。
- **注释**：在 `coalesce` 内新增中文注释说明为何保守处理。

### 2. 配套仓库 `netlist-to-sch-via-skidl`（与本 fork 联用）

- **`convert_netlist.py`**：`--schematic-subdir` 默认值由 `kicad_generated` 改为 **`kicad_generated_h`**，与当前注入的 `human_readable=True` 流程一致。
- **`generated_script_patch.py`**：`_finalize_generated_skidl` 默认 `schematic_subdir` 改为 **`kicad_generated_h`**。
- **`.gitignore`**：增加 `kicad_generated_h/`；保留 `kicad_generated/` 以兼容旧产物。
- **示例 `*_skidl.py` / README**：原理图输出路径改为 **`kicad_generated_h`** 说明。

### 3. 验收

- 在 `ski2` 环境下对 `5micro_3.net` 重新 `convert_netlist` 后运行 `5micro_3_skidl.py`，**`human_readable=True`** 应能完成 schematic 生成（或进入既有 auto_stub 回退），且 `.kicad_sch` 位于 **`kicad_generated_h/`**。

---

## 2026-05-16 更新：connected group 几何对齐后处理（仅 `human_readable=True`）

### 目的

在既有「主器件 + 角色分区」启发式摆放之后，补一层**保守的几何整理**，缓解「器件聚在一起但不在一条线上」的问题：主干共线、上下支路分层、左右近似对称，且不破坏默认可用性。

### 修改文件

| 文件 | 说明 |
|------|------|
| `src/skidl/schematics/place.py` | 新增对齐后处理及调用点 |
| `update.md` | 本记录 |

**未改** `route.py`（本步仅 placement 后处理）。

### 新增 / 调整函数（`Placer` 内）

| 函数 | 作用 |
|------|------|
| `_placement_ctr(part)` | 取 `place_bbox * tx` 中心，供对齐计算 |
| `_set_part_center_y` / `_set_part_center_x` | 单轴平移并吸附 `GRID` |
| `_identify_trunk_parts` | 主器件 + 非 `power`/`decoupling` 的直接邻居 → 主干候选 |
| `_align_connected_geometry` | 四步后处理：主干共 Y → 上下支路 `y_top`/`y_bottom` → 同 role/度数成对镜像 → 最多 25 轮支路垂直去重叠 |

### 调用时机

- **仅** **`place_connected_parts_rowbased`** 且 `human_readable=True`：分区摆放完成后、`snap_to_grid` 之前调用。
- **不**对 `place_connected_parts` 小组（&lt;20 器件，力导向）调用——例如 `4micro2`（6 器件）若强行对齐会把多颗 LED 压到同一水平线，路由 `coalesce` 时出现 `TerminalClashException`。

### 2026-05-16 修补（`TerminalClash`）

| 调整 | 原因 |
|------|------|
| 取消小组力导向路径上的对齐 | `4micro2` 等 &lt;20 器件电路不走 rowbased，对齐反而破坏力导向结果 |
| 主干仅含**已在同一水平带**的近邻 | 避免“所有直接邻居”共 Y |
| 支路/对称 Y 对齐前做**重叠检测**，冲突则跳过 | 不制造 bbox 重叠 |
| 对称只统一 **Y**，不再镜像 **X** | 避免引脚落到同一路由坐标 |
| 去重叠对**全组**开放，必要时水平微移 | 主干之间也能拉开 |

### 为什么这样改

- 分区启发式已决定「谁在上/下/左/右」，但**未强制几何共线**；后处理只调中心坐标，不动主器件锚点，改动面小、可回滚。
- 主干识别复用 `_classify_part_role` 与邻接图，避免随机选链；排序统一用 `_part_ref_key`。
- `branch_gap` 由 `max(place_bbox.h)`、`BLK_INT_PAD`、`GRID` 推导，避免写死过激间距。
- 对称仅对「同 role + 同连接度」且分居主干两侧的支路器件成对处理，避免对单一 case 硬编码。

### 默认行为

- **`human_readable=False`（默认）**：**不变**；不调用 `_align_connected_geometry`。
- **`human_readable=True`**：仅上述 connected parts 路径多一步几何整理。

### 风险与限制

- 第一版**优先水平主干**（统一 Y）；竖向主干未单独识别。
- `power` / `decoupling` / `connector` 不参与上下支路 Y 吸附，保留分区启发式位置（避免左侧纵向连接器被压成一行）；不参与主干共线。
- 对称与分层是**启发式近似**，复杂拓扑（多分叉、非两侧对称）只能做到「更整齐」，非最优布局。
- 去重叠仅沿 Y 小步推开支路器件，若 X 方向严重重叠可能需后续路由/人工微调。
- NetTerminal 在对齐**之后**再 `place_net_terminals`，避免终端标签拉动整体几何。

### 自检

- `python -m compileall src/skidl/schematics/place.py` 通过。

---

## 2026-05-16 更新：small connected group 弱美化（新文件）

### 为什么 small 组不能照搬大组强对齐

- 小组（`real_count <= _ROW_PLACE_THRESHOLD`，默认 20）走 **`place_connected_parts` 力导向**，拓扑已由弹簧布局拉开。
- 大组 rowbased 路径上的 `_align_connected_geometry`（主干共线、上下分层、成对 Y 统一）适合**分区启发式之后**的结构化整理，**不适合**直接套在力导向结果上：容易把多颗器件强压到同一水平带，引脚在路由 grid 上共位，触发 `TerminalClashException`（如 `4micro2`）。

### 为什么要拆到新文件

- 避免 `place.py` 继续堆叠后处理逻辑；**大组强对齐留在 `place.py`**，**小组弱美化独立维护**。
- 便于单独回滚、测试与阅读。

### 新文件与入口

| 项 | 值 |
|----|-----|
| 新文件 | `src/skidl/schematics/place_small_group.py` |
| 入口函数 | `beautify_small_connected_group(...)` |

### `place.py` 集成（最小改动）

在 `place_connected_parts` 中，仅当 **`human_readable=True`** 且 **`real_count <= _ROW_PLACE_THRESHOLD`**（即未进入 rowbased）时：

1. `evolve_placement`（及可选 `rotate_parts` 重跑）之后  
2. `place_net_terminals` 之前  

调用 `beautify_small_connected_group`，再对 real parts `snap_to_grid`。

大组 rowbased + `_align_connected_geometry` **不变**。

### 核心策略（弱规则 / 去抖）

1. **方向**：组 bbox 宽 ≥ 高 → 偏横向，仅做 **Y 向**微调；纵向小图第一版不动。  
2. **水平带分簇**：中心 Y 相差 ≤ `2 * GRID` 的器件划为一带；**仅对 ≥2 颗的带**做吸附。  
3. **弱吸附**：目标 Y 为带内中位数并 snap；单颗移动量 ≤ `2 * GRID`；移动前/后做风险检查。  
4. **可选 pair**：同 role 或同 ref 前缀、尺寸接近、分居中线两侧且 Y 已很近 → 仅轻微统一 Y（**无 X 镜像**）。  
5. **去重叠**：最多 15 轮，优先沿 **X** 小步（因主调整为 Y），每步经安全检查。

### 风险控制

| 检查 | 说明 |
|------|------|
| bbox | 移动后与其它 real part 的 `place_bbox * tx` 相交则回滚 |
| 引脚拥挤 | 已连接引脚的 `place_pt * tx`：不同 net 过近，或同轴距离 < `GRID` 则放弃移动 |
| 幅度限制 | 只修“本来就接近”的（带内 / ≤ `2*GRID`），不重建拓扑 |
| 单轴 | 横向图只主调 Y，不同时大幅改 X+Y |
| 确定性 | 全程 `part_ref_key` 稳定排序，无随机 |

### 默认行为

- **`human_readable=False`（默认）**：**不变**，不调用 `beautify_small_connected_group`。  
- **`human_readable=True` 且大组（>20）**：仍只走 rowbased + `_align_connected_geometry`，**不**走本模块。  
- **`human_readable=True` 且小组（≤20）**：力导向后多一步弱美化。

---

## 2026-05-17 更新：human_readable 走线局部凸起压平（仅 `route.py`）

### 修的是哪类问题

- **现象**：small schematic / `human_readable=True` 时，走线里常出现「本可水平或垂直连过去，中间却多一小段台阶/凸起」——整体 route 没错，是 cleanup 未把局部可拉直的折线继续压平。
- **不是 placement 问题**：器件位置与分区启发式无关；根因是 global/switchbox 路由优先连通、`create_nonpin_terminals()` 离散采样产生 dogleg，以及 `remove_jogs()` 主要针对标准三段 staircase/tophat，对「两平行主线 + 短 offset」类小 detour 覆盖不足。

### 修改文件

| 文件 | 说明 |
|------|------|
| `src/skidl/schematics/route.py` | `cleanup_wires()` 内新增 `_straighten_local_detours()` |
| `update.md` | 本记录 |

**未改** `place.py`、`place_small_group.py`、global/switchbox 主路由算法。

### 新增 pass：`_straighten_local_detours()`

- **接入位置**：`cleanup_wires()` 中，每个 net 的 `remove_jogs()` **之后**；仍走原有 `merge_segments()` → `split_segments()` → `trim_stubs()` 循环，把结果收干净。
- **模式**：**仅 `human_readable=True`** 时调用；默认 `human_readable=False` **不执行**，行为与改动前一致。
- **策略（保守）**：
  - 只处理 **H-V-H** / **V-H-V** 三元组，中间为短正交连接、两侧为同向主线；
  - **情况 A**：两侧主线已共线 → 尝试用 **单段** 替代三段；
  - **情况 B**：高度/宽度差 ≤ `max(GRID, 2*GRID)` → 尝试用 **L 形两段** 绕开中间台阶（角点顺序固定排序，保证确定性）；
  - 每次至多改一处，改完返回由外层 while 继续 merge/split/trim（与 `remove_jogs` 相同节奏）。

### 安全检查

| 检查 | 说明 |
|------|------|
| 器件阻挡 | 新线段 bbox 不得与 `part_bboxes` 相交 |
| 其它 net | 与同轨其它 net 线段 overlay 视为阻挡（与 `remove_jogs` 相同逻辑） |
| pin | 中间拐角接 pin 则跳过；本 net 落在旧路径上的 pin 必须仍落在新路径上 |
| 范围 | 仅小 detour（阈值 `max(GRID, 2*GRID)`），不重写整网几何 |

### 默认行为

- **`human_readable=False`（默认）**：**不变**；不调用 `_straighten_local_detours()`。
- **`human_readable=True`**：在既有 `remove_jogs` + `humanize_wires` 流程中多一步局部压平，不改变路由主流程与 seed 策略。

### 自检

- `python -m compileall src/skidl/schematics/route.py` 通过。

---

## 2026-05-17 补充：junction-aware 局部凸起压平（仍仅 `route.py`）

### 为什么原先纯三段检测不够

- 第一版 `_straighten_local_detours()` 要求 `mid` 两端各**恰好**再连一条同 net segment（`len(others)==1`），等价于假设凸起是孤立 H-V-H / V-H-V 三元组。
- 真实 cleanup 后 wire 往往已 `split_segments` / `add_junctions`，端点常是 **T 分叉、短 stub、同 net 多段共点**；小凸起两端已是 junction，旧逻辑直接 `continue`，凸起残留。

### 为什么 junction-aware case 很常见

- `remove_jogs` 与 merge/split 会在拐角处留下额外正交分支；global/switchbox 路由也不会保证 degree-2 拓扑。
- 视觉上仍是「两平行主线 + 短 offset」，但拓扑上端点已挂分支，**不是** placement 问题，而是 cleanup 后图结构更复杂。

### 本次扩展（不放宽安全检查）

| 项 | 说明 |
|----|------|
| 主通路选取 | `main_legs_at()` 在 junction 上按方向筛平行侧腿，**确定性**排序后枚举 `(seg_a, seg_c)` 候选 |
| 分支保留 | `attachment_points_ok()`：待移除段与**保留**同 net 段的交汇点必须仍落在新路径上；「有分支」不再一律跳过 |
| 仍保守 | part / other-net obstruction、pin 落点、小 detour 阈值、每次只改一处、仅 `human_readable=True` — **均未放宽** |
| 跨 net | 仍只读写当前 net 的 `segments`；其它 net 仅通过既有 `obstructed()` 同轨 overlay 检查 |

### 默认行为

- **`human_readable=False`**：**不变**。
- **`human_readable=True`**：在既有 pass 上扩大可压平范围；不确定拓扑时 `try_apply` 失败即跳过。
