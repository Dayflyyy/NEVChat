import timesfm

# 设置参数并加载模型
tfm = timesfm.TimesFm(
    context_len=512,  # 例如，使用最大长度512的上下文
    horizon_len=12,   # 预测未来12个月的销量
    input_patch_len=32,
    output_patch_len=128,
    num_layers=20,
    model_dims=1280,
    backend="cpu",    # 如果有GPU，可以改为 "gpu"
)

# 从Hugging Face加载模型
tfm.load_from_checkpoint(repo_id="google/timesfm-1.0-200m")

import pandas as pd

# 设置频率为 "M" 表示月度数据
forecast_df = tfm.forecast_on_df(
    inputs=input_df,
    freq="M",  # 月频率
    value_name="y",
    num_jobs=-1,  # 使用多线程加速
)