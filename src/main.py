import sys
import pkgutil
import importlib
import logging
import argparse
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
    logger.info("🚀 Starting multi-module automated check with sliding block...")
    
    total_lines = len(lines)
    
    for line_num in range(1, total_lines + 1):
        idx = line_num - 1
        block = []
        
        for i in range(idx - 5, idx):
            if i < 0:
                block.append(None)
            else:
                block.append(lines[i])
                
        block.append(lines[idx])
        
        for i in range(idx + 1, idx + 6):
            if i >= total_lines:
                block.append(None)
            else:
                block.append(lines[i])

        for rule_func in checker.rules:
            try:
                error_msg = rule_func(block)
                if error_msg:
                    logger.warning(
                        f"\n❌ Line {line_num} triggered rule {rule_func.__name__}\n{error_msg}\n::error file={input_path},line={line_num}::{error_msg}"
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

    parser = argparse.ArgumentParser(description="Run checker on text or file")
    parser.add_argument("-i", "--input", help="input file path", required=True)
    args = parser.parse_args()

    # ===== path setup =====
    SRC_DIR = Path(__file__).resolve().parent

    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    from registry import checker

    load_rules_from_dir('module')

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    sample_text = input_path.read_text(encoding="utf-8")

    run_check(sample_text)
