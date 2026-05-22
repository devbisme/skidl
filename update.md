# skidl-pnr-opt 更新记录

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
