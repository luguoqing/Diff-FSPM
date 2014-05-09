#!/bin/bash
# Update on: Apr 28, 2014
# Author: Lu Guoqing <guoqing@nfs.iscas.ac.cn>

# ========== 注意：===============
# 运行机器上必须装有 epydoc 工具
# ================================

# 导入环境变量
# source ~/.bashrc

# 定位到上层目录
cd ..
echo "[INFO]enter dir: $(pwd)"

# 最终结果
final_ret=0

# 挨个运行所有cfg文件
for cfg in update_epydoc/conf/*; do
	epydoc --parse-only --config "$cfg" -v -v
	
	if [ $? -ne 0 ]; then
		echo "[ERROR]update epydoc failed: $cfg"
		final_ret=1
	fi
done

echo "[INFO]Final Ret: $final_ret"
exit $final_ret
