"""職種別選択傾向分析モジュール"""
import pandas as pd
import numpy as np
from utils import logger

def analyze_job_type_preferences(df):
    """
    職種別の選択傾向をより詳細に分析する関数
    
    Args:
        df: 分析対象のデータフレーム (1列目: 職種, 2列目: 回答者数, 3列目以降: 各選択肢の選択数)
        
    Returns:
        dict: 職種ごとの選択傾向分析結果
    """
    try:
        # CSVの形式が想定通りかチェック
        if len(df.columns) < 3:
            logger.warning("CSVのフォーマットが期待と異なります。少なくとも3列以上が必要です。")
            return {"error": "CSVのフォーマットが期待と異なります。少なくとも3列以上が必要です。"}
        
        # デバッグ用に最初の数行を出力
        logger.info(f"職種別詳細分析の入力データ（最初の3行）:\n{df.iloc[:3, :].to_string()}")
        
        # 職種が1列目、回答者数が2列目、選択肢が3列目以降と想定
        job_types = df.iloc[:, 0]
        total_responses = df.iloc[:, 1]
        choice_columns = df.columns[2:]
        choices = df.iloc[:, 2:]
        
        # 選択肢の列名をログに出力
        logger.info(f"選択肢の列名: {list(choice_columns)}")
        
        # 全職種の平均選択率を計算（ベースラインとして）
        overall_choice_rates = {}
        for i, choice_col in enumerate(choice_columns):
            try:
                # 各選択肢の全体平均選択率
                total_choice = choices.iloc[:, i].sum()
                total_resp = total_responses.sum()
                if total_resp > 0:
                    overall_choice_rates[choice_col] = (total_choice / total_resp) * 100
                else:
                    overall_choice_rates[choice_col] = 0
            except Exception as e:
                logger.warning(f"全体平均選択率の計算中にエラー ({choice_col}): {str(e)}")
                overall_choice_rates[choice_col] = 0
        
        logger.info(f"全体の平均選択率: {overall_choice_rates}")
        
        # 結果を格納する辞書
        job_type_preferences = {}
        
        # 各職種について分析
        for i, job_type in enumerate(job_types):
            if pd.isna(job_type) or str(job_type).strip() == "":
                continue
                
            # この職種の回答者数
            try:
                response_count = float(total_responses.iloc[i])
                if pd.isna(response_count) or response_count <= 0:
                    logger.warning(f"職種 {job_type} の回答者数が無効です: {total_responses.iloc[i]}")
                    continue
            except Exception as e:
                logger.warning(f"職種 {job_type} の回答者数の変換中にエラー: {str(e)}")
                continue
                
            # この職種の選択傾向データ
            job_preference = {
                "response_count": response_count,
                "choice_rates": {},
                "relative_preferences": {},
                "top_choices": [],
                "distinctive_choices": []
            }
            
            # 各選択肢の選択率を計算
            for j, choice_col in enumerate(choice_columns):
                try:
                    choice_count = float(choices.iloc[i, j])
                    if pd.isna(choice_count):
                        choice_count = 0
                        
                    # 選択率を計算
                    choice_rate = (choice_count / response_count) * 100
                    job_preference["choice_rates"][choice_col] = round(choice_rate, 1)
                    
                    # 全体平均との相対比較
                    overall_rate = overall_choice_rates.get(choice_col, 0)
                    if overall_rate > 0:
                        relative_preference = (choice_rate / overall_rate) - 1  # -1で相対的な選好度に変換
                        job_preference["relative_preferences"][choice_col] = round(relative_preference * 100, 1)  # パーセント表示
                    else:
                        job_preference["relative_preferences"][choice_col] = 0
                    
                except Exception as e:
                    logger.warning(f"職種 {job_type} の選択肢 {choice_col} の計算中にエラー: {str(e)}")
                    job_preference["choice_rates"][choice_col] = 0
                    job_preference["relative_preferences"][choice_col] = 0
            
            # トップの選択肢を特定
            sorted_choices = sorted(
                job_preference["choice_rates"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            job_preference["top_choices"] = sorted_choices[:3]  # 上位3つ
            
            # 特徴的な選択肢を特定（全体平均と比較して際立つもの）
            sorted_distinctive = sorted(
                job_preference["relative_preferences"].items(),
                key=lambda x: abs(x[1]),  # 絶対値で並べ替え（正負どちらも重要）
                reverse=True
            )
            job_preference["distinctive_choices"] = sorted_distinctive[:3]  # 最も特徴的な3つ
            
            # 結果を辞書に追加
            job_type_preferences[str(job_type)] = job_preference
        
        # 結果をロギング
        logger.info(f"職種別詳細分析の結果: {len(job_type_preferences)}件の職種を分析しました")
        
        return job_type_preferences
        
    except Exception as e:
        logger.error(f"職種別詳細選択傾向の分析中にエラーが発生しました: {str(e)}")
        return {"error": f"職種別詳細選択傾向の分析中にエラーが発生しました: {str(e)}"}

def generate_job_type_insights(job_type_preferences):
    """
    職種別選択傾向から洞察を生成する関数
    
    Args:
        job_type_preferences: analyze_job_type_preferences関数からの結果
        
    Returns:
        dict: 職種ごとの洞察文
    """
    if not job_type_preferences or isinstance(job_type_preferences, dict) and "error" in job_type_preferences:
        return job_type_preferences
    
    insights = {}
    
    for job_type, preference_data in job_type_preferences.items():
        try:
            insight_parts = []
            
            # トップの選択肢から洞察を生成
            if "top_choices" in preference_data and preference_data["top_choices"]:
                top1 = preference_data["top_choices"][0]
                top1_name, top1_rate = top1
                
                # 主要な選択肢の特徴
                if top1_rate > 50:
                    insight_parts.append(f"{job_type}は「{top1_name}」を特に重視する傾向が強く（{top1_rate}%）")
                elif top1_rate > 30:
                    insight_parts.append(f"{job_type}は「{top1_name}」を重視する傾向があり（{top1_rate}%）")
                else:
                    insight_parts.append(f"{job_type}は「{top1_name}」をある程度重視し（{top1_rate}%）")
                
                # 2番目の選択肢（あれば）
                if len(preference_data["top_choices"]) > 1:
                    top2 = preference_data["top_choices"][1]
                    top2_name, top2_rate = top2
                    
                    # 1位との差に基づいて表現を変える
                    if abs(top1_rate - top2_rate) < 10:
                        insight_parts.append(f"同様に「{top2_name}」も重視しています（{top2_rate}%）")
                    else:
                        insight_parts.append(f"次いで「{top2_name}」を評価しています（{top2_rate}%）")
            
            # 特徴的な選択肢から洞察を生成
            if "distinctive_choices" in preference_data and preference_data["distinctive_choices"]:
                distinctive = preference_data["distinctive_choices"][0]
                distinctive_name, distinctive_rate = distinctive
                
                # 他の職種と比較して特徴的な選択肢
                if distinctive_rate > 50:
                    insight_parts.append(f"他の職種と比較して「{distinctive_name}」を顕著に重視する特徴があります（平均より{distinctive_rate}%高い）")
                elif distinctive_rate > 20:
                    insight_parts.append(f"他の職種よりも「{distinctive_name}」を重視する傾向があります（平均より{distinctive_rate}%高い）")
                elif distinctive_rate < -50:
                    insight_parts.append(f"他の職種と比較して「{distinctive_name}」をほとんど重視しない特徴があります（平均より{abs(distinctive_rate)}%低い）")
                elif distinctive_rate < -20:
                    insight_parts.append(f"他の職種よりも「{distinctive_name}」を重視しない傾向があります（平均より{abs(distinctive_rate)}%低い）")
            
            # 選択肢の内容に基づく特性の推測
            if "top_choices" in preference_data and preference_data["top_choices"]:
                top1_name = preference_data["top_choices"][0][0]
                
                # 選択肢の名前に基づいて、職種の特性を推測
                if "コスト" in top1_name or "価格" in top1_name or "費用" in top1_name:
                    insight_parts.append("コスト意識が高い傾向にあります")
                elif "効率" in top1_name or "生産性" in top1_name:
                    insight_parts.append("業務効率を重視する傾向にあります")
                elif "品質" in top1_name or "精度" in top1_name:
                    insight_parts.append("品質や精度を最優先する特徴があります")
                elif "革新" in top1_name or "先進" in top1_name or "新技術" in top1_name:
                    insight_parts.append("新しい技術や革新的なアプローチに関心が高いです")
                elif "安全" in top1_name or "セキュリティ" in top1_name:
                    insight_parts.append("安全性やセキュリティを重視する傾向があります")
                elif "使いやすさ" in top1_name or "操作性" in top1_name:
                    insight_parts.append("使いやすさやユーザビリティを重視しています")
            
            # 最終的な洞察テキストを生成
            if insight_parts:
                insights[job_type] = "、".join(insight_parts) + "。"
            else:
                insights[job_type] = f"{job_type}の選択傾向に明確な特徴は見られませんでした。"
                
        except Exception as e:
            logger.error(f"職種 {job_type} の洞察生成中にエラー: {str(e)}")
            insights[job_type] = f"{job_type}の傾向分析中にエラーが発生しました。"
    
    return insights

def get_choice_correlation_matrix(df):
    """
    選択肢間の相関関係を分析する
    
    Args:
        df: 分析対象のデータフレーム
        
    Returns:
        pd.DataFrame: 相関行列
    """
    try:
        # 選択肢のデータだけを取得（3列目以降）
        choices_df = df.iloc[:, 2:]
        
        # 各行の合計（各職種の総回答数）
        row_totals = df.iloc[:, 1]
        
        # 選択肢を選択率に変換
        choice_rates = pd.DataFrame()
        for col in choices_df.columns:
            choice_rates[col] = choices_df[col] / row_totals
        
        # 相関行列を計算
        corr_matrix = choice_rates.corr()
        
        return corr_matrix
        
    except Exception as e:
        logger.error(f"選択肢相関分析中にエラー: {str(e)}")
        return pd.DataFrame()

def get_strongest_correlations(corr_matrix, top_n=5):
    """
    最も強い相関関係を持つ選択肢ペアを特定する
    
    Args:
        corr_matrix: 相関行列
        top_n: 返す上位ペア数
        
    Returns:
        list: (選択肢1, 選択肢2, 相関係数)のタプルのリスト
    """
    try:
        # 相関行列の上三角部分を取得
        corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                corr = corr_matrix.iloc[i, j]
                corr_pairs.append((col1, col2, corr))
        
        # 絶対値で並べ替え
        sorted_pairs = sorted(corr_pairs, key=lambda x: abs(x[2]), reverse=True)
        
        return sorted_pairs[:top_n]
        
    except Exception as e:
        logger.error(f"強相関ペア特定中にエラー: {str(e)}")
        return []

def analyze_choice_patterns(df):
    """
    選択肢の組み合わせパターンを分析する
    
    Args:
        df: 分析対象のデータフレーム
        
    Returns:
        dict: 選択肢の組み合わせパターン分析結果
    """
    try:
        # 相関行列を取得
        corr_matrix = get_choice_correlation_matrix(df)
        
        # 最も強い相関関係を持つペアを取得
        strongest_correlations = get_strongest_correlations(corr_matrix, top_n=5)
        
        # 結果をフォーマット
        result = {
            "positive_correlations": [],
            "negative_correlations": []
        }
        
        for col1, col2, corr in strongest_correlations:
            correlation_info = {
                "choice1": col1,
                "choice2": col2,
                "correlation": round(corr, 2)
            }
            
            if corr > 0:
                result["positive_correlations"].append(correlation_info)
            else:
                result["negative_correlations"].append(correlation_info)
        
        return result
        
    except Exception as e:
        logger.error(f"選択パターン分析中にエラー: {str(e)}")
        return {"error": str(e)}

def interpret_choice_patterns(pattern_analysis):
    """
    選択肢パターン分析結果から洞察を生成する
    
    Args:
        pattern_analysis: analyze_choice_patterns関数からの結果
        
    Returns:
        str: 分析洞察の文章
    """
    if "error" in pattern_analysis:
        return f"選択肢パターンの分析中にエラーが発生しました: {pattern_analysis['error']}"
    
    insights = []
    
    # 正の相関関係（一緒に選ばれやすい組み合わせ）
    if pattern_analysis["positive_correlations"]:
        insights.append("選択肢の選好傾向を分析すると、以下の組み合わせが一緒に重視される傾向があります：")
        for i, corr_info in enumerate(pattern_analysis["positive_correlations"][:3]):
            insights.append(f"- 「{corr_info['choice1']}」と「{corr_info['choice2']}」（相関係数: {corr_info['correlation']}）")
    
    # 負の相関関係（相反する選択肢）
    if pattern_analysis["negative_correlations"]:
        insights.append("一方、以下の組み合わせは相反する傾向があります（一方を重視する職種は他方をあまり重視しない）：")
        for i, corr_info in enumerate(pattern_analysis["negative_correlations"][:3]):
            insights.append(f"- 「{corr_info['choice1']}」と「{corr_info['choice2']}」（相関係数: {corr_info['correlation']}）")
    
    # LPへの示唆
    insights.append("")
    insights.append("これらの相関パターンから、LP設計では、正の相関を持つ選択肢については、同じターゲット層に対して一緒にアピールすることが効果的です。一方、負の相関を持つ選択肢については、異なるセグメントのターゲットに分けて訴求することで、それぞれの関心に合わせたメッセージが届きやすくなります。")
    
    return "\n".join(insights)
