---
name: ui-performance
description: "让 React 或 Vue 界面的交互又快又顺：先测量再优化，守住 INP、长任务、帧率和包体积的预算，修掉卡顿、多余重渲染、布局抖动和大列表。写交互界面、审查界面代码或用户说卡、慢、掉帧时使用。Use when building or reviewing interactive React or Vue UI, or when an interface feels slow, janky, or drops frames."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。

# 界面交互性能

交互慢是 bug。每个交互都要马上有反馈，动画不能掉帧。先测量，找到真正的瓶颈，再改；改完再测一次证明变快了。

## 预算

| 指标 | 目标 |
|---|---|
| INP（交互到下一次绘制） | p75 < 200 ms，目标 < 100 ms |
| 点击到视觉反馈 | < 100 ms，按下态立即出现 |
| 主线程长任务 | 交互路径上没有 > 50 ms 的任务 |
| 动画 | 稳定 60 fps，只动 `transform` 和 `opacity` |
| CLS | < 0.1 |
| LCP | < 2.5 s |
| 首屏 JS | 按路由拆分，首屏 gzip 后尽量 < 170 KB |

## 先测量

1. 在生产构建下测，开发模式的数字不算。在 DevTools 里把 CPU 降速 4×，模拟中端设备。
2. Chrome Performance 面板录下那次交互，看长任务、强制同步布局（紫色 Layout 带红角）、脚本耗时。
3. React 用 React DevTools Profiler，开「Highlight updates」，看哪些组件在不该渲染时渲染了。Vue 用 Vue DevTools 的 Performance 和组件渲染时间线。
4. 线上用 `web-vitals` 采集 INP、LCP、CLS，看 p75。
5. 包体积用 `vite-bundle-visualizer` 或 `rollup-plugin-visualizer`。

需要在真浏览器里自动录制和对比时，用 `control-ui`。报数字前过一遍 `benchmark-checklist`。

## 常见问题和修法

### 渲染太多

- React：状态放在用到它的最低层；把频繁变化的状态和大子树分开；昂贵子树用 `memo`，传给它的回调和对象用 `useCallback`、`useMemo` 稳住。用了 React Compiler 就不手写这些。Context 按变化频率拆开，不要一个大 Context。
- Vue：大对象和不需要深层响应的数据用 `shallowRef`、`markRaw`；列表项用 `v-memo`；计算放 `computed`，不要放模板里的方法调用；props 传稳定引用。
- 列表 key 用稳定 ID，不用下标。

### 交互里的重活

- 先给反馈，再做重活：React 用 `useTransition`、`useDeferredValue` 把非紧急更新降级；Vue 先更新按下态，重计算放到 `nextTick` 之后或拆块。
- 超过 50 ms 的计算拆块（`scheduler.yield()`，不支持时 `setTimeout(0)` 分片），或者放进 Web Worker。
- 输入框搜索做防抖，滚动和 resize 处理用 `requestAnimationFrame` 节流，监听器加 `{ passive: true }`。

### 布局抖动

- 不要在同一帧里先写样式再读 `offsetHeight`、`getBoundingClientRect`；先批量读，再批量写。
- 图片、视频、广告位预留尺寸（`width`/`height` 或 `aspect-ratio`），避免 CLS。
- 长页面区块用 `content-visibility: auto` 加 `contain-intrinsic-size`。

### 大列表和大数据

- 超过约 100 行就虚拟化：React 用 `@tanstack/react-virtual`，Vue 用 `@tanstack/vue-virtual` 或 `vue-virtual-scroller`。
- 分页或无限滚动在服务端做，不要一次拉全量。

### 动画

- 只动 `transform`、`opacity`；不动 `width`、`height`、`top`、`left`、`box-shadow`。
- 尊重 `prefers-reduced-motion`。
- 动画细节和设计取舍交给 `impeccable`。

### 加载

- 路由级代码拆分（`React.lazy`、Vue 的异步组件和路由懒加载）；重组件（编辑器、图表）按需加载。
- 数据请求用缓存和去重（TanStack Query、SWR、Pinia 加缓存），悬停或可见时预取。
- 乐观更新让提交类交互立即生效，失败再回滚。

## 交付

1. 优化前的测量：工具、条件（生产构建、降速倍数）、数字。
2. 找到的瓶颈和原因。
3. 改动。
4. 优化后用同样条件再测的数字。没变快就回退，换方向。
