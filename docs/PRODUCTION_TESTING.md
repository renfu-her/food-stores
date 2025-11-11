# 使用生产环境URL进行高并发测试

## 快速开始

### 1. 混合负载测试（推荐，相对安全）

```bash
python test/test_concurrent_load.py \
  --base-url https://quick-foods.ai-tracks.com \
  --concurrent 50 \
  --requests 500 \
  --timeout 30
```

### 2. 产品查询压力测试（只读操作，最安全）

```bash
python test/test_concurrent_load.py \
  --base-url https://quick-foods.ai-tracks.com \
  --concurrent 100 \
  --requests 2000 \
  --timeout 30
```

### 3. 库存竞争条件测试（⚠️ 会创建真实订单）

```bash
python test/test_concurrent_load.py \
  --stock-test \
  --base-url https://quick-foods.ai-tracks.com \
  --shop-id 1 \
  --product-id 1 \
  --initial-stock 10 \
  --concurrent-orders 20 \
  --timeout 30
```

## 参数说明

- `--base-url`: API基础URL（必需）
- `--concurrent`: 并发用户数（默认: 50）
- `--requests`: 总请求数（默认: 1000）
- `--timeout`: 请求超时时间，秒（默认: 30）
- `--no-verify-ssl`: 禁用SSL证书验证（仅用于测试环境，生产环境不推荐）

## 注意事项

⚠️ **重要警告**:
1. **生产环境测试**: 在生产环境运行测试可能会影响真实用户，请谨慎使用
2. **数据影响**: 库存测试会创建真实订单，可能影响库存数据
3. **服务器负载**: 高并发测试会给服务器带来压力，建议在低峰期进行
4. **监控资源**: 测试时请监控服务器CPU、内存、数据库连接数等
5. **逐步增加**: 从低并发开始，逐步增加并发数

## 推荐测试流程

1. **先进行轻量级测试**:
   ```bash
   python test/test_concurrent_load.py --base-url https://quick-foods.ai-tracks.com --concurrent 10 --requests 100
   ```

2. **观察结果**，如果正常，逐步增加:
   ```bash
   python test/test_concurrent_load.py --base-url https://quick-foods.ai-tracks.com --concurrent 50 --requests 500
   ```

3. **进行压力测试**:
   ```bash
   python test/test_concurrent_load.py --base-url https://quick-foods.ai-tracks.com --concurrent 100 --requests 2000
   ```

## 查看结果

测试完成后会生成JSON格式的结果文件：
- 文件名格式: `test_results_YYYYMMDD_HHMMSS.json`
- 包含详细的成功率、响应时间、错误信息等

## 使用Shell脚本（推荐）

也可以使用提供的Shell脚本进行交互式测试：

```bash
chmod +x test/test_production.sh
./test/test_production.sh
```

