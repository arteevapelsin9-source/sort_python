import multiprocessing
import os
import tempfile
import shutil

def split_file(file_name, chunk_size): # делим начальный файл на чанки
    chunks = [] # список имен временных файлов для каждого чанка
    with open(file_name, 'r') as f:
        batch = [] # для накопления чисел текущего чанка
        for line in f:
            line = line.strip() # если есть лишние пробелы или переносы
            if line:
                batch.append(line + '\n')
                if len(batch) >= chunk_size:
                    # создем временный файл так, чтобы он сам не удалялся, и сохраняем на диск
                    tmp = tempfile.NamedTemporaryFile(delete=False, mode='w+t')
                    tmp.writelines(batch)
                    tmp.close()
                    chunks.append(tmp.name) # добавляем имя вр.файла в список
                    batch = []
        if batch: # для последнего батча, если он не набрал 10000 чисел и не пустой
            tmp = tempfile.NamedTemporaryFile(delete=False, mode='w+t')
            tmp.writelines(batch)
            tmp.close()
            chunks.append(tmp.name)
    return chunks

def sort_chunk(chunk_file): # сортируем один чанк
    with open(chunk_file, 'r') as f:
        lines = f.readlines() # читаем все строки, тк чанк маленький
    lines.sort(key=lambda x: int(x.strip())) # сортируем по возрастанию
    with open(chunk_file, 'w') as f:
        f.writelines(lines)
    return chunk_file

def merge_two(f1, f2, out): # соединяем 2 отсортированных файла
    with open(f1) as a, open(f2) as b, open(out, 'w') as c:
        line_a, line_b = a.readline(), b.readline() # тут уже читаем построчно, а не всё сразу
        while line_a and line_b:
            # сравниваем числа из входных файлов
            if int(line_a.strip()) <= int(line_b.strip()):
                c.write(line_a)
                line_a = a.readline()
            else:
                c.write(line_b)
                line_b = b.readline()
        # хотя бы один из файлов точно закончился, то надо записать остаток из второго
        while line_a:
            c.write(line_a) 
            line_a = a.readline()
        while line_b:
            c.write(line_b) 
            line_b = b.readline()

def merge_all(files): # соединяем все файлы, пока не останется один
    while len(files) > 1:
        new_files = [] # создаём список для файлов, чтобы иих соединять
        for i in range(0, len(files), 2):
            if i + 1 < len(files):
                tmp = tempfile.NamedTemporaryFile(delete=False, mode='w+t')
                tmp.close() # создаем пустой файл для merge_two
                merge_two(files[i], files[i+1], tmp.name) # вызываем merge_two
                new_files.append(tmp.name)
                os.unlink(files[i]) # удаляем отработавшие файлы
                os.unlink(files[i+1])
            else:
                new_files.append(files[i]) # если файл без пары, то он просто переходит на следующую итерацию
        files = new_files
    return files[0] # получаем отсортированный файл

def sort_large_file(filename, chunk_size=10000):
    chunks = split_file(filename, chunk_size) # вызываем для разбития на чанки split_file
    print(f"{len(chunks)} sozdano")
    with multiprocessing.Pool() as pool: # сортируем чанки на ядрах (параллельно), вызывая на каждом sort_chunk
        chunks = pool.map(sort_chunk, chunks)
    # получаем итоговый временный файл и сохраняем его как txt
    result = merge_all(chunks)
    output = 'sorted_' + filename
    shutil.move(result, output)
    print(f"Rezultat in {output}")

if __name__ == '__main__':
    sort_large_file('random_numbers.txt')

