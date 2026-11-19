---
name: remotion-create
description: "「用 Remotion 做视频」「做可重复渲染的产品演示」。用 React 编排镜头、字幕和音轨，并导出视频。Use when creating or extending a Remotion video composition."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。

# 用 Remotion 制作视频

按 [Remotion 官方文档](https://www.remotion.dev/docs/) 编写的中文流程。适合产品演示、教程片头和需要改数据后重新渲染的视频。

## 准备工程

先检查仓库中是否已有 Remotion 项目。已有项目沿用现有依赖和包管理器。新项目在合适的空目录或新子目录里创建，命令和参数以 [官方建项目说明](https://www.remotion.dev/docs/create-video) 为准。查明目标画幅、帧率、时长和素材来源后列出镜头，每个镜头写明起止时间和主要信息。

## 编排镜头

1. 用 `Composition` 声明画幅、总帧数、帧率和可配置输入。用 `Sequence` 定位镜头，按帧计算字幕、转场和动画。动画随当前帧变化，避免依赖 CSS 时间、定时器或外部请求的返回顺序。
2. 把图片、字体和音轨放进项目资源目录，本地素材按项目约定引用。为视频边缘、字幕和不同画幅留出空间。在镜头切换处检查相邻帧，确认层级和叠加音频符合预期。
3. 用 [Remotion Studio](https://www.remotion.dev/docs/studio) 检查构图和节奏，再按 [渲染文档](https://www.remotion.dev/docs/cli/render) 用项目内的 Remotion CLI 导出。抽查导出文件的开头、结尾和转场，核对尺寸、总时长、字幕和声音，交付工程入口和实际输出路径。
