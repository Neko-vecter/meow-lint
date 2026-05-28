import sys
import pkgutil
import importlib
import logging
from pathlib import Path

def load_rules_from_dir(package_name):

    rules_path = SRC_DIR / package_name
    
    if not rules_path.exists():
        logger.error(f"❌ Cannot find rules directory: {rules_path}")
        return

    logger.info(f"🔍 Loading rules from path: {rules_path}")

    for _, module_name, _ in pkgutil.iter_modules([str(rules_path)]):
        full_module_name = f"{package_name}.{module_name}"
        try:
            importlib.import_module(full_module_name)
            logger.info(f"✅ Automatically loaded rule component: {full_module_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load component: {full_module_name}", exc_info=True)


def run_check(text):
    lines = text.splitlines()
    logger.info("🚀 Starting multi-module automated check...")
    
    for line_num, line in enumerate(lines, start=1):
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        for rule_func in checker.rules:
            try:
                error_msg = rule_func(cleaned_line)
                if error_msg:
                    logger.warning(
                        f"\n❌ Line {line_num} triggered rule {rule_func.__name__}\n{error_msg}"
                    )
            except Exception as e:
                logger.error(f"❌ {rule_func.__name__} {e}")

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger(__name__)

    SRC_DIR = Path(__file__).resolve().parent

    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    else:
        from registry import checker

    load_rules_from_dir('module')

    sample_text = """
    ## 1.x 核心业务流程
    ##1.1 漏了空格的标题
    """
    run_check(sample_text)
