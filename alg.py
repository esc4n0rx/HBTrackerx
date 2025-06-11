import random
import time
import statistics
from typing import List, Any, Tuple

class AdaptiveHybridSort:
    def __init__(self):
        self.SMALL_ARRAY_THRESHOLD = 50
        self.TIMSORT_THRESHOLD = 0.7  # 70% já ordenado
        self.DUPLICATES_THRESHOLD = 0.3  # 30% duplicatas
    
    def sort(self, arr: List[Any]) -> List[Any]:
        """Função principal que escolhe a estratégia de ordenação"""
        if len(arr) <= 1:
            return arr.copy()
        
        # Análise inicial dos dados
        analysis = self._analyze_data(arr)
        
          
        strategy = self._choose_strategy(analysis, len(arr))
        
        # Aplicar a estratégia escolhida
        return self._apply_strategy(arr.copy(), strategy, analysis)
    
    def _analyze_data(self, arr: List[Any]) -> dict:
        """Analisa as características dos dados"""
        n = len(arr)
        analysis = {
            'size': n,
            'ordered_ratio': 0,
            'duplicate_ratio': 0,
            'data_type': type(arr[0]).__name__ if arr else 'unknown',
            'range_info': None,
            'chosen_strategy': None
        }
        
        # Para arrays grandes, usar amostragem mais cuidadosa
        if n > 2000:
            sample_size = min(1000, n // 10)  # Amostra maior
            indices = sorted(random.sample(range(n), sample_size))
            sample = [arr[i] for i in indices]
        else:
            sample = arr.copy()
        
        # Verificar ordenação parcial
        ordered_pairs = 0
        for i in range(len(sample) - 1):
            if sample[i] <= sample[i + 1]:
                ordered_pairs += 1
        analysis['ordered_ratio'] = ordered_pairs / max(1, len(sample) - 1)
        
        # Verificar duplicatas
        unique_count = len(set(sample))
        analysis['duplicate_ratio'] = 1 - (unique_count / len(sample))
        
        # Informações de range para números - usar array completo para counting sort
        if isinstance(arr[0], (int, float)) and n <= 10000:  # Só para arrays menores
            try:
                min_val = min(arr)  # Array completo, não amostra
                max_val = max(arr)
                range_size = max_val - min_val + 1
                
                # Só usar counting sort se o range for razoável
                if range_size <= n * 2 and range_size <= 100000:
                    analysis['range_info'] = {
                        'min': min_val,
                        'max': max_val,
                        'range': range_size
                    }
            except (TypeError, ValueError):
                pass  # Não é numérico comparável
        
        return analysis
    
    def _choose_strategy(self, analysis: dict, size: int) -> str:
        """Escolhe a melhor estratégia baseada na análise"""
        if size < self.SMALL_ARRAY_THRESHOLD:
            analysis['chosen_strategy'] = 'insertion'
            return 'insertion'
        
        if analysis['ordered_ratio'] >= self.TIMSORT_THRESHOLD:
            analysis['chosen_strategy'] = 'timsort'
            return 'timsort'
        
        if analysis['duplicate_ratio'] >= self.DUPLICATES_THRESHOLD:
            analysis['chosen_strategy'] = 'three_way_quicksort'
            return 'three_way_quicksort'
        
        if (analysis['range_info'] is not None and 
            analysis['data_type'] in ['int']):
            analysis['chosen_strategy'] = 'counting_sort'
            return 'counting_sort'
        
        analysis['chosen_strategy'] = 'introsort'
        return 'introsort'
    
    def _apply_strategy(self, arr: List[Any], strategy: str, analysis: dict) -> List[Any]:
        """Aplica a estratégia escolhida"""
        if strategy == 'insertion':
            return self._insertion_sort(arr)
        elif strategy == 'timsort':
            return self._adaptive_timsort(arr)
        elif strategy == 'three_way_quicksort':
            return self._three_way_quicksort(arr)
        elif strategy == 'counting_sort':
            return self._counting_sort(arr, analysis['range_info'])
        else:  # introsort
            return self._introsort(arr)
    
    def _insertion_sort(self, arr: List[Any]) -> List[Any]:
        """Insertion sort otimizado para arrays pequenos"""
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            # Busca binária para encontrar posição
            left, right = 0, i
            while left < right:
                mid = (left + right) // 2
                if arr[mid] <= key:
                    left = mid + 1
                else:
                    right = mid
            
            # Mover elementos
            for k in range(i, left, -1):
                arr[k] = arr[k - 1]
            arr[left] = key
        
        return arr
    
    def _adaptive_timsort(self, arr: List[Any]) -> List[Any]:
        """Versão simplificada do Timsort para dados parcialmente ordenados"""
        if len(arr) <= 1:
            return arr
            
        # Encontrar runs (sequências ordenadas)
        runs = self._find_runs(arr)
        
        # Se há apenas um run, já está ordenado
        if len(runs) <= 1:
            return arr
        
        # Merge runs usando uma pilha
        while len(runs) > 1:
            # Merge os dois últimos runs
            last_run = runs.pop()
            second_last_run = runs.pop()
            
            # Fazer merge dos dados
            start1, end1 = second_last_run
            start2, end2 = last_run
            
            left_part = arr[start1:end1]
            right_part = arr[start2:end2]
            merged = self._merge(left_part, right_part)
            
            # Colocar de volta no array
            arr[start1:end2] = merged
            
            # Adicionar o novo run merged
            runs.append((start1, end2))
        
        return arr
    
    def _find_runs(self, arr: List[Any]) -> List[Tuple[int, int]]:
        """Encontra sequências já ordenadas"""
        if len(arr) <= 1:
            return [(0, len(arr))]
            
        runs = []
        start = 0
        
        while start < len(arr):
            end = start + 1
            
            if end >= len(arr):
                runs.append((start, len(arr)))
                break
                
            # Determinar se é crescente ou decrescente
            if arr[start] <= arr[end - 1]:
                # Run crescente
                while end < len(arr) and arr[end - 1] <= arr[end]:
                    end += 1
            else:
                # Run decrescente - encontrar e reverter
                while end < len(arr) and arr[end - 1] > arr[end]:
                    end += 1
                # Reverter o run decrescente
                arr[start:end] = reversed(arr[start:end])
            
            runs.append((start, end))
            start = end
        
        return runs
    
    def _three_way_quicksort(self, arr: List[Any]) -> List[Any]:
        """Quicksort de 3 vias para muitas duplicatas"""
        if len(arr) <= 1:
            return arr
        self._three_way_quicksort_recursive(arr, 0, len(arr) - 1)
        return arr
    
    def _three_way_quicksort_recursive(self, arr: List[Any], low: int, high: int):
        """Implementação recursiva do 3-way quicksort"""
        if low >= high:
            return
        
        lt, gt = self._three_way_partition(arr, low, high)
        self._three_way_quicksort_recursive(arr, low, lt - 1)
        self._three_way_quicksort_recursive(arr, gt + 1, high)
    
    def _three_way_partition(self, arr: List[Any], low: int, high: int) -> Tuple[int, int]:
        """Partição de 3 vias (< pivot, = pivot, > pivot)"""
        pivot = arr[low]
        i = low + 1
        lt = low
        gt = high
        
        while i <= gt:
            if arr[i] < pivot:
                arr[lt], arr[i] = arr[i], arr[lt]
                lt += 1
                i += 1
            elif arr[i] > pivot:
                arr[i], arr[gt] = arr[gt], arr[i]
                gt -= 1
            else:
                i += 1
        
        return lt, gt
    
    def _counting_sort(self, arr: List[int], range_info: dict) -> List[int]:
        """Counting sort para inteiros com range pequeno"""
        if not range_info:
            # Fallback para introsort se não temos info de range
            return self._introsort(arr)
        
        min_val = range_info['min']
        max_val = range_info['max']
        range_size = range_info['range']
        
        # Verificação de segurança
        if range_size <= 0 or range_size > 1000000:
            return self._introsort(arr)
        
        count = [0] * range_size
        
        # Contar ocorrências com verificação de bounds
        for num in arr:
            if isinstance(num, int) and min_val <= num <= max_val:
                count[num - min_val] += 1
            else:
                # Se encontramos um valor fora do range, usar introsort
                return self._introsort(arr)
        
        # Reconstruir array ordenado
        result = []
        for i in range(range_size):
            if count[i] > 0:
                result.extend([i + min_val] * count[i])
        
        return result
    
    def _introsort(self, arr: List[Any]) -> List[Any]:
        """Introsort (híbrido de quicksort e heapsort)"""
        if len(arr) <= 1:
            return arr
        max_depth = 2 * len(arr).bit_length()
        self._introsort_recursive(arr, 0, len(arr) - 1, max_depth)
        return arr
    
    def _introsort_recursive(self, arr: List[Any], low: int, high: int, max_depth: int):
        """Implementação recursiva do introsort"""
        if low >= high:
            return
            
        size = high - low + 1
        if size < self.SMALL_ARRAY_THRESHOLD:
            self._insertion_sort_range(arr, low, high)
        elif max_depth == 0:
            self._heapsort_range(arr, low, high)
        else:
            pivot = self._partition(arr, low, high)
            self._introsort_recursive(arr, low, pivot - 1, max_depth - 1)
            self._introsort_recursive(arr, pivot + 1, high, max_depth - 1)
    
    def _partition(self, arr: List[Any], low: int, high: int) -> int:
        """Partição do quicksort com mediana-de-três"""
        if high - low < 2:
            return low
            
        mid = (low + high) // 2
        
        # Mediana de três
        if arr[mid] < arr[low]:
            arr[low], arr[mid] = arr[mid], arr[low]
        if arr[high] < arr[low]:
            arr[low], arr[high] = arr[high], arr[low]
        if arr[high] < arr[mid]:
            arr[mid], arr[high] = arr[high], arr[mid]
        
        arr[mid], arr[high] = arr[high], arr[mid]
        pivot = arr[high]
        
        i = low - 1
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
        
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    def _insertion_sort_range(self, arr: List[Any], low: int, high: int):
        """Insertion sort para um range específico"""
        for i in range(low + 1, high + 1):
            key = arr[i]
            j = i - 1
            while j >= low and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
    
    def _heapsort_range(self, arr: List[Any], low: int, high: int):
        """Heapsort para um range específico"""
        # Construir heap
        size = high - low + 1
        for i in range(size // 2 - 1, -1, -1):
            self._heapify(arr, low, high, low + i)
        
        # Extrair elementos do heap
        for i in range(high, low, -1):
            arr[low], arr[i] = arr[i], arr[low]
            self._heapify(arr, low, i - 1, low)
    
    def _heapify(self, arr: List[Any], start: int, end: int, root: int):
        """Heapify para heapsort"""
        while True:
            largest = root
            left = 2 * (root - start) + 1 + start
            right = 2 * (root - start) + 2 + start
            
            if left <= end and arr[left] > arr[largest]:
                largest = left
            if right <= end and arr[right] > arr[largest]:
                largest = right
            
            if largest == root:
                break
            
            arr[root], arr[largest] = arr[largest], arr[root]
            root = largest
    
    def _merge(self, left: List[Any], right: List[Any]) -> List[Any]:
        """Merge para timsort"""
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result


# Função de teste e benchmark melhorada
def test_adaptive_sort():
    """Testa o algoritmo com diferentes tipos de dados"""
    sorter = AdaptiveHybridSort()
    
    test_cases = [
        # Array pequeno
        ([64, 34, 25, 12, 22, 11, 90], "Array pequeno"),
        
        # Array já ordenado
        (list(range(1000)), "Array já ordenado"),
        
        # Array com muitas duplicatas
        ([1, 3, 2, 1, 3, 2, 1, 3, 2] * 100, "Muitas duplicatas"),
        
        # Array aleatório menor para testar
        (random.sample(range(1000), 500), "Array aleatório"),
        
        # Array quase ordenado
        (list(range(500)) + random.sample(range(500, 600), 50), "Quase ordenado"),
        
        # Array com range pequeno
        ([random.randint(1, 50) for _ in range(1000)], "Range pequeno"),
        
        # Array reverso
        (list(range(1000, 0, -1)), "Array reverso"),
        
        # Array com alguns elementos grandes
        ([1, 2, 3, 1000000, 4, 5, 6], "Range muito grande")
    ]
    
    print("=== Teste do Algoritmo Adaptativo Híbrido ===\n")
    
    total_speedup = []
    
    for test_data, description in test_cases:
        print(f"Testando: {description} (tamanho: {len(test_data)})")
        
        # Testar correção
        original = test_data.copy()
        
        # Nosso algoritmo
        start_time = time.time()
        sorted_result = sorter.sort(test_data.copy())
        our_time = time.time() - start_time
        
        # Verificar se está correto
        expected = sorted(original)
        is_correct = sorted_result == expected
        
        print(f"  ✓ Correto: {is_correct}")
        print(f"  ⏱ Nosso tempo: {our_time * 1000:.2f}ms")
        
        # Comparar com sorted() nativo
        start_time = time.time()
        python_sorted = sorted(original)
        python_time = time.time() - start_time
        
        print(f"  ⏱ Python sorted(): {python_time * 1000:.2f}ms")
        
        if our_time > 0:
            speedup = python_time / our_time
            total_speedup.append(speedup)
            if speedup > 1:
                print(f"  🚀 {speedup:.2f}x mais rápido que sorted()")
            elif speedup < 1:
                print(f"  🐌 {1/speedup:.2f}x mais lento que sorted()")
            else:
                print(f"  ⚖️ Mesma velocidade que sorted()")
        
        # Mostrar estratégia escolhida
        analysis = sorter._analyze_data(original)
        strategy = sorter._choose_strategy(analysis, len(original))
        print(f"  📊 Estratégia: {strategy}")
        print(f"  📈 Ordenação: {analysis['ordered_ratio']:.1%}, Duplicatas: {analysis['duplicate_ratio']:.1%}")
        
        if not is_correct:
            print(f"  ❌ ERRO: Resultado incorreto!")
            print(f"     Esperado: {expected[:10]}...")
            print(f"     Obtido:   {sorted_result[:10]}...")
        
        print()
    
    if total_speedup:
        avg_speedup = sum(total_speedup) / len(total_speedup)
        print(f"📊 Speedup médio: {avg_speedup:.2f}x")

if __name__ == "__main__":
    test_adaptive_sort()