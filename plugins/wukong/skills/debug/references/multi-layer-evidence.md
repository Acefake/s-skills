# 多层系统取证

跨CI、构建、签名等组件时，逐个边界观察实际输入、输出和配置是否传播。先定位第一次偏差，再修改；不要把所有层一起改。

每个边界回答：

1. 接收到什么输入，输出是否符合下一层的约定？
2. 必要配置是否存在，是否被正确加载？
3. 哪个状态第一次与正常路径不同？

例如签名失败时，依次核对CI是否提供配置、构建进程是否收到、签名身份是否存在、实际签名命令怎样失败。敏感配置只记录存在性或脱敏后的标识，不打印密钥。

```bash
if [ -n "${IDENTITY:-}" ]; then
  echo "signing identity configured"
else
  echo "signing identity missing"
fi
security find-identity -v
codesign --sign "$IDENTITY" --verbose=4 "$APP"
```

这是macOS签名场景的示例，不是每次调试都要运行的固定脚本。使用当前系统的对应工具，保留失败日志；日志只能证明检查实际覆盖的层。
