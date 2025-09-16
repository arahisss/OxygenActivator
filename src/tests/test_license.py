import pytest
from unittest.mock import Mock, MagicMock, patch
from src.license_key import gen_license_key

RUNS = list(range(1, 31))
test_results = []

@pytest.mark.parametrize("run_number", RUNS)
def test_gen_license_key(run_number):
    successful_runs = 0
    failed_runs = 0

    try:
        mock_pbar = Mock()
        result = gen_license_key(mock_pbar)

        success = result is not None and isinstance(result, str) and len(result.strip()) > 0
        status = "SUCCESS" if success else "FAILED"

        test_results.append({
            'run': run_number,
            'status': status,
            'key': result
        })
    except Exception as e:
        failed_runs += 1
        status = f"ERROR: {e}"
        test_results.append({
            'run': run_number,
            'status': status,
            'key': result
        })
    assert success, f"Запуск {run_number} вернул некорректный результат: {repr(result)}"


def write_results_to_file(results):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"license_key_test_{timestamp}.txt"

    successful_runs = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed_runs = len(results) - successful_runs

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("ТЕСТ ГЕНЕРАЦИИ ЛИЦЕНЗИОННЫХ КЛЮЧЕЙ (30 запусков)\n")
        f.write("=" * 70 + "\n")
        f.write(f"Дата теста: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Успешных запусков: {successful_runs}/30\n")
        f.write(f"Неудачных запусков: {failed_runs}/30\n")
        f.write(f"Процент успеха: {(successful_runs / 30) * 100:.1f}%\n")
        f.write("=" * 70 + "\n\n")

        for result in results:
            f.write(f"ЗАПУСК #{result['run']:2d} - {result['status'].upper()}\n")
            f.write(f"Ключ: {result['key']}\n")
            f.write("-" * 50 + "\n")

    print(f"\nВсе результаты записаны в файл: {filename}")

@pytest.fixture(scope="session", autouse=True)
def summarize_results(request):
    yield
    if test_results:
        write_results_to_file(test_results)


# def test_single_run():
#     mock_pbar = Mock()
#
#     result = gen_license_key(mock_pbar)
#
#     assert result is not None, "Функция вернула None"
#     assert isinstance(result, str), "Результат должен быть строкой"
#     assert len(result.strip()) > 0, "Ключ не должен быть пустым"
#
#     print(f"Одиночный тест: УСПЕХ")
#     print(f"Длина ключа: {len(result)} символов")
#     print(f"Ключ: {result}")
