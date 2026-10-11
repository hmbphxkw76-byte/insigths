"""
测试新增的三个数据管道和对应分析方法
"""
import io
import sys

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_new_pipe_registration():
    """测试新管道是否注册成功"""
    from src.data_engine import get_runner
    runner = get_runner()
    pipes = runner.list_pipes()
    expected_new_pipes = ["cross_cultural_adaptation", "salary_negotiation_tactics", "professional_certification_path"]
    for pipe_id in expected_new_pipes:
        assert pipe_id in pipes, f"管道 {pipe_id} 未注册"
    print(f"✅ 测试1通过：新管道注册成功，当前共 {len(pipes)} 条管道")

def test_new_pipe_collection():
    """测试新管道数据采集功能"""
    from src.data_engine import get_runner
    runner = get_runner()
    params = {"country_code": "AE", "profession": "cybersecurity"}
    
    # 测试跨文化适应管道
    df1 = runner.run_single("cross_cultural_adaptation", params)
    assert df1 is not None and not df1.empty, "跨文化适应管道采集失败"
    assert "adaptation_phase" in df1.columns, "跨文化适应管道缺少必要列"
    
    # 测试薪资谈判管道
    df2 = runner.run_single("salary_negotiation_tactics", params)
    assert df2 is not None and not df2.empty, "薪资谈判管道采集失败"
    assert "negotiation_phase" in df2.columns, "薪资谈判管道缺少必要列"
    
    # 测试资格认证管道
    df3 = runner.run_single("professional_certification_path", params)
    assert df3 is not None and not df3.empty, "资格认证管道采集失败"
    assert "career_level" in df3.columns, "资格认证管道缺少必要列"
    
    print("✅ 测试2通过：新管道数据采集正常")

def test_new_analysis_methods():
    """测试新分析方法是否生效"""
    from src.prompt_runtime import PromptRuntime
    runner = PromptRuntime()
    
    # 检查新的分析方法是否存在
    assert hasattr(runner, '_method_cross_cultural_adaptation_analysis'), "跨文化适应分析方法不存在"
    assert hasattr(runner, "_method_salary_negotiation_analysis"), "薪资谈判分析方法不存在"
    assert hasattr(runner, "_method_certification_path_analysis"), "资格认证分析方法不存在"
    
    # 测试方法调用
    from src.prompt_runtime import SectionResult, PromptDefinition
    s = SectionResult(
        dimension_id="cross_cultural_adaptation",
        label_zh="跨文化适应路径指南",
        label_en="Cross-Cultural Adaptation Pathway Guide",
        method="cross_cultural_adaptation"
    )
    p = PromptDefinition(
        id="test",
        label_zh="测试",
        label_en="Test"
    )
    runner._method_cross_cultural_adaptation_analysis(s, p)
    assert len(s.insights) > 0, "跨文化适应分析方法未生成洞察"
    
    s2 = SectionResult(
        dimension_id="salary_negotiation",
        label_zh="薪资谈判话术与策略",
        label_en="Salary Negotiation Tactics & Scripts",
        method="salary_negotiation"
    )
    runner._method_salary_negotiation_analysis(s2, p)
    assert len(s2.insights) > 0, "薪资谈判分析方法未生成洞察"
    
    s3 = SectionResult(
        dimension_id="certification_path",
        label_zh="职业资格认证全路径",
        label_en="Professional Certification Roadmap",
        method="certification_path"
    )
    runner._method_certification_path_analysis(s3, p)
    assert len(s3.insights) > 0, "资格认证分析方法未生成洞察"
    
    print("✅ 测试3通过：新分析方法运行正常")

def test_yaml_config():
    """测试YAML配置文件更新正确"""
    import yaml
    with open("prompts/industry/profession_country.yaml", "r", encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f)
    
    # 检查维度数量是否为18
    assert "18大维度" in yaml_data["description"]["zh"], "YAML描述中维度数量未更新"
    assert "18 dimensions" in yaml_data["description"]["en"], "YAML英文描述中维度数量未更新"
    
    # 检查新的管道配置是否存在
    pipe_ids = [p["pipe"] for p in yaml_data["data_pipes"]]
    expected_new_pipes = ["cross_cultural_adaptation", "salary_negotiation_tactics", "professional_certification_path"]
    for pipe_id in expected_new_pipes:
        assert pipe_id in pipe_ids, f"YAML中不存在 {pipe_id} 管道配置"
    
    # 检查新的分析维度是否存在
    dim_ids = [d["id"] for d in yaml_data["analysis_dimensions"]]
    expected_new_dims = ["cross_cultural_adaptation", "salary_negotiation", "certification_path"]
    for dim_id in expected_new_dims:
        assert dim_id in dim_ids, f"YAML中不存在 {dim_id} 分析维度"
    
    # 检查新的报告章节是否存在
    sections = yaml_data["report"]["format"]["sections"]
    expected_new_sections = ["cross_cultural_adaptation", "salary_negotiation", "certification_path"]
    for section in expected_new_sections:
        assert section in sections, f"YAML中不存在 {section} 报告章节"
    
    print("✅ 测试4通过：YAML配置文件更新正确")

def test_source_attribution_english():
    """测试数据来源是否为全英文"""
    from src.data_engine import get_runner
    runner = get_runner()
    params = {"country_code": "AE", "profession": "cybersecurity"}
    
    # 获取三个新管道的数据源
    pipe_ids = ["cross_cultural_adaptation", "salary_negotiation_tactics", "professional_certification_path"]
    for pipe_id in pipe_ids:
        factory = runner._pipe_registry.get(pipe_id)
        assert factory is not None, f"{pipe_id} 未注册"
        pipe = factory()
        sources = pipe.source_attribution()
        assert len(sources) > 0, f"{pipe_id} 无数据来源"
        # 检查是否包含中文
        for src in sources:
            assert not any('\u4e00' <= c <= '\u9fff' for c in src), f"{pipe_id} 数据来源包含中文：{src}"
    
    print("✅ 测试5通过：数据来源全英文，无中文来源")

if __name__ == "__main__":
    print("="*60)
    print("新增功能全链路测试")
    print("="*60)
    
    try:
        test_new_pipe_registration()
        test_new_pipe_collection()
        test_new_analysis_methods()
        test_yaml_config()
        test_source_attribution_english()
        
        print("="*60)
        print(f"🎉 所有 {5} 项测试全部通过！")
        print("="*60)
    except AssertionError as e:
        print(f"❌ 测试失败：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试异常：{e}")
        sys.exit(1)