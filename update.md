# skidl-pnr-opt 更新记录

## Power net 导出：GND_0 / VCC_5V_0 不再变成 global_label

**日期**：2026-05-26  
**范围**：`schematics/power_net.py`（新）、`place.py`、`topology/mcu.py`、`tools/kicad9/sexp_schematic.py`、`tools/kicad6–9/gen_schematic.py`

### 问题现象

TG032-MCU 等 Altium 导入电路中，`GND_0`、`VCC_5V_0` 等分区电源网在原理图上显示为普通 `global_label`，而同图的 `GND` 却正确显示为 `power:GND` 符号。

### 根因

布局、auto_stub、sexp 导出三套 power 识别规则不一致：

| 阶段 | 旧行为 |
|------|--------|
| `place._is_power_net_name` | 子串匹配，`GND_0` 可识别 |
| `gen_schematic._POWER_NET_RE` | 整名精确匹配，`GND_0` 不识别 |
| `sexp net_label_to_sexp` | 仅当网名 **等于** KiCad power 库 symbol 名时才导出 power symbol |

此外 `mcu_stub_remaining_signal_nets` 会把未本地布线的 power 网 stub 成 label，加剧上述导出问题。

### 修改点

1. 新增 [`schematics/power_net.py`](src/skidl/schematics/power_net.py)：
   - `is_power_net_name(name)` — 统一 power-like 识别
   - `resolve_power_symbol_shape(name)` — 映射 KiCad power 库 **外形**（如 `GND_0` → `GND`，`VCC_5V_0` → `+5V`）
   - `resolve_power_symbol_value(name)` — 始终返回原始网名（Value 字段）
2. `place._is_power_net_name` 委托上述 helper。
3. `auto_stub_nets`（kicad6–9）改用 `is_power_net_name`，不再维护窄 `_POWER_NET_RE` 匹配路径。
4. `kicad9/sexp_schematic.py`：`lib_id` 用 shape，`Value` 用原网名；边界 sheet pin 跳过逻辑同步。
5. `mcu_stub_remaining_signal_nets`：power 网 stub 时注明导出走 power symbol，而非 signal global_label。

### 风险

- **不修改 SKiDL `Net.name`**，不改网表电气连接。
- 外形映射失败时仍 fallback `global_label`。
- `GND` 与 `GND_0` 的 power symbol **Value 不同**，KiCad 中仍为独立网名，不会把不同电源域短接。

### 验收

`tests/unit_tests/test_power_net.py`；TG032-MCU 生成后 sch 中无 `(global_label "GND_0")` / `(global_label "VCC_5V_0")`，出现 `lib_id "power:GND"` + `Value "GND_0"` 等。

### 2026-05-26 修订（悬空 power symbol）

根因：用户命名 power 网仍创建 `NetTerminal`，摆在 bbox 顶边；power 导出改为 symbol 后，顶边 `#PWR001`/`#PWR002` 无导线悬空。

修订：`sch_node.add_circuit` 对 `is_power_net_name` 不建 NetTerminal；`sexp _net_terminal_label_to_sexp` 对 power 网直接返回 None。TG032 器件数 39→35（去掉 4 个边缘 NetTerminal）。

---

## generic_driver 水平 power rail（布局 + 预布线）

**日期**：2026-05-21  
**范围**：`topology.py`、`route.py`（必要时 `place.py` 仅透传 options）

### 功能

在 `human_readable=True` 且拓扑识别为 **generic_driver**（`fallback=False`）时：

1. **布局**（`build_driver_rail_plan` / `apply_driver_rail_safe_placement`）
   - 根据全部器件 `place_bbox` 计算顶/底水平走廊 `top_y` / `bottom_y` 与 `x_min`/`x_max`
   - 顶网（VCC/VIN/W+/LED+ 等）器件放在顶 rail **下方**；底网（GND/W-/LED- 等）放在底 rail **上方**
   - 主功率链（C/D → U → L → 连接器）横排在两条 rail **之间**，不压在 rail 线上
   - 控制网（PWM/DIM/EN）不进入长 rail，支路放在主控右侧中部

2. **预布线**（`route_driver_rails`）
   - 对 `rail_plan.top_nets` / `bottom_nets` 画水平 `Segment`，各 pin 短竖 stub 接入
   - 不经过 switchbox；这些网从 `global_router` / `switchbox_router` 的 `routed_nets` 中排除
   - 内部匿名网 `Net-(...)` 不参与 rail；`NetTerminal` 引脚不作为 stub 端点

### 日志（`schematic_progress=True`）

```text
[schematic] driver rail placement ...
[schematic] driver rails: top=[...], bottom=[...], top_y=..., bottom_y=..., x=(..., ...)
[schematic] driver rail blocker: ref=... bbox=... rail=top|bottom
[schematic] driver rail pre-route: N nets [...]
```

### 关闭 / 回退

| 选项 | 默认 | 效果 |
|------|------|------|
| `driver_rail_routing=False` | `True` | 不生成 `node._driver_rail_plan`，不 rail-safe 布局，不预布线 |
| `topology_detection=False` | `True` | 不走 generic_driver 专用逻辑 |
| `human_readable=False` | — | 全部 rail 逻辑关闭 |

未识别为 generic_driver 或 `fallback=trunk_aware` 时仍使用原有 trunk-aware + switchbox 布线。

### 验收参考

TG032-WH / PT4115：LED+/W+ 顶部长水平线，GND/LED-/W- 底部长水平线；主控 U 不被长线穿过；L 与输出连接器在右侧；PWM/DIM 为短支路。

### 2026-05-21 修订（TG032 绕框问题）

根因：仅预布了 `/LED+`、`GND`、`/LED-`，**`Net-(D1-A)` / `Net-(D1-K)` 仍走 switchbox**，且 R1 不在主链行、去耦电容被甩远、`cleanup_wires` 对 rail 网做 split/去 jog。

修订：

- 主链行纳入卫星件（R1 等），`Net-(D1-*)` 用 **chain local 水平母线** 预布线
- 布线前 **重算** `top_y`/`bottom_y`（与 expansion 后坐标一致）
- LED 去耦电容贴在 U2 右侧、两 rail 之间
- `_driver_prerouted_nets` 跳过 cleanup 的 jog/split
- `auto_stub` 会把 GND/LED± 标成 label-only；`restore_driver_wire_nets` 在布线前恢复保留网
- cleanup 第一轮也必须跳过 prerouted（此前会 `trim_stubs` 把预布线删光 → 原理图“无线”）
