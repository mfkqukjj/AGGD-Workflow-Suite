import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_account_pool(size=100):
    """生成固定大小的账号池，30%为微信号格式"""
    accounts = []
    for _ in range(size):
        if random.random() < 0.3:
            # 生成微信号格式: wxid_ + 19位随机字符
            wxid = f"wxid_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=19))}"
            accounts.append(wxid)
        else:
            # 生成普通账号
            accounts.append(f"{''.join(random.choices('0123456789', k=16))}")
    return accounts

def generate_random_bank_card():
    # 生成随机银行卡号
    return f"{''.join(random.choices('0123456789', k=16))}"

def generate_random_order_id():
    # 生成随机订单号
    return f"ORDER{''.join(random.choices('0123456789ABCDEF', k=12))}"

def generate_random_merchant_name():
    """生成随机商户名，30%为个人商户"""
    if random.random() < 0.3:
        # 生成个人商户名称
        first_names = '张王李赵周吴郑黄'
        last_names = '伟明俊杰强晶婷静'
        name = random.choice(first_names) + random.choice(last_names)
        return f"{name}（个人）"
    else:
        # 生成企业商户名称
        prefix = random.choice(['北京', '上海', '广州', '深圳', '杭州'])
        type_name = random.choice(['科技', '贸易', '商务', '电子', '网络'])
        suffix = random.choice(['有限公司', '股份公司', '商贸公司'])
        return f"{prefix}{type_name}{suffix}"

def generate_account_pairs(size=100):
    """生成固定大小的账号对，每对包含一个支付账号和对应的微信号"""
    account_pairs = []
    for _ in range(size):
        payment_account = f"{''.join(random.choices('0123456789', k=16))}"
        wx_account = f"wxid_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=19))}"
        account_pairs.append((payment_account, wx_account))
    return account_pairs

def generate_test_data(num_records=3000):
    # 创建日期范围
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    # 生成账号对池
    account_pairs = generate_account_pairs(50)
    # 创建支付账号到微信号的映射
    payment_to_wx = {pair[0]: pair[1] for pair in account_pairs}
    
    # 先生成借贷标志和交易双方
    borrow_lend = [random.choice(['借', '贷']) for _ in range(num_records)]
    payer_accounts = []
    receiver_accounts = []
    query_accounts = []
    
    for i in range(num_records):
        # 随机选择两个不同的账号对作为交易双方
        payer_pair, receiver_pair = random.sample(account_pairs, 2)
        payer_accounts.append(payer_pair[0])
        receiver_accounts.append(receiver_pair[0])
        
        # 根据借贷标志确定对应的支付账号
        payment_account = payer_pair[0] if borrow_lend[i] == '借' else receiver_pair[0]
        
        # 随机决定是否使用微信号作为查询账号
        if random.random() < 0.3:
            query_accounts.append(payment_to_wx[payment_account])
        else:
            query_accounts.append(payment_account)
    
    # 生成基础数据
    data = {
        '查询账号': query_accounts,
        '付款方支付帐号': payer_accounts,
        '收款方支付帐号': receiver_accounts,
        '支付机构内部订单号': [generate_random_order_id() for _ in range(num_records)],
        '交易时间': [(start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )).strftime('%Y%m%d%H%M%S') for _ in range(num_records)],
        '借贷标志': borrow_lend,
        '交易金额': [round(random.uniform(100, 10000), 2) for _ in range(num_records)],
        '交易余额': [round(random.uniform(1000, 100000), 2) for _ in range(num_records)],
        '付款方银行卡号': [generate_random_bank_card() for _ in range(num_records)],
        '收款方银行卡号': [generate_random_bank_card() for _ in range(num_records)],
        '交易类型': [random.choice(['转账', '支付', '充值', '提现']) for _ in range(num_records)],
        '收款方的商户名称': [generate_random_merchant_name() for _ in range(num_records)],
        '备注': [random.choice(['日常交易', '商品购买', '服务费用', '付款成功', '转账成功']) for _ in range(num_records)]
    }
    
    df = pd.DataFrame(data)
    
    # 保存账号映射关系
    mapping_data = {
        '支付账号': [pair[0] for pair in account_pairs],
        '微信号': [pair[1] for pair in account_pairs]
    }
    mapping_df = pd.DataFrame(mapping_data)
    
    return df, mapping_df

def main():
    # 创建输出目录
    output_dir = 'test_data'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成3份数据
    for i in range(3):
        df, mapping_df = generate_test_data(1000)
        output_file = os.path.join(output_dir, f'test_data_{i+1}.xlsx')
        mapping_file = os.path.join(output_dir, f'account_mapping_{i+1}.xlsx')
        
        df.to_excel(output_file, index=False)
        mapping_df.to_excel(mapping_file, index=False)
        
        print(f'已生成测试数据文件: {output_file}')
        print(f'已生成账号映射文件: {mapping_file}')

if __name__ == '__main__':
    main()