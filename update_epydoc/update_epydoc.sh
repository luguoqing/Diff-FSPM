#!/bin/bash
# Update on: Apr 28, 2014
# Author: Lu Guoqing <guoqing@nfs.iscas.ac.cn>

# ========== ע�⣺===============
# ���л����ϱ���װ�� epydoc ����
# ================================

# ���뻷������
# source ~/.bashrc

# ��λ���ϲ�Ŀ¼
cd ..
echo "[INFO]enter dir: $(pwd)"

# ���ս��
final_ret=0

# ������������cfg�ļ�
for cfg in update_epydoc/conf/*; do
	epydoc --parse-only --config "$cfg" -v -v
	
	if [ $? -ne 0 ]; then
		echo "[ERROR]update epydoc failed: $cfg"
		final_ret=1
	fi
done

echo "[INFO]Final Ret: $final_ret"
exit $final_ret
