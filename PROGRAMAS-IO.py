import sys
import numpy as np
from fractions import Fraction
#*****

#import pandas as pd
from pandas_ods_reader import read_ods

#Importar el script creado:
from task import *


try:
    import pandas as pd
    pandas_av = True
except ImportError:
    pandas_av = False
    pass

product_names = []
col_values = []
z_equation = []
final_rows = []
solutions = []
x = 'X'
z2_equation = []
removable_vars = []
no_solution = """
        ---ERROR ----
Revise las restricciones e intente nuevamente
            """


def main():
    global decimals
    global const_num, prod_nums
    #prob_type = int(1)
    print("""
    PROGRAMAS - ROSA MERA
    1 = Método Simplex
    2 = Proyecto (PERT-CPM)
    """)
    #######
    try:
        prob_type = int(input("Ingrese el número del programa que desea abrir: >"))
    except ValueError:
        print("Por favor ingrese un número")
        prob_type = int(input("Ingrese el número del programa que desea abrir: >"))
    if prob_type != 2 and prob_type != 1 and prob_type != 0:
        sys.exit("Ha ingresado un número incorrecto ->" + str(prob_type))
    
    if prob_type == 2:
        #Para archivos con extensión .ods:
        mydata = read_ods("data.ods", "Sheet1")
        #Para archivos con extensión .xlsx descomentar la siguiente línea eliminando el #:
        #mydata = pd.read_excel(io = "data.xlsx",sheet_name = "Sheet1")
        #Calcular la ruta crítica
        mydata = computeCPM(mydata)
        printTask(mydata)
        #Numero de tareas
        ntask = mydata.shape[0]

        #Método de la ruta crítica
        cp = []
        for i in range(ntask):
            if(mydata['MTi,j'][i] == 0):
                cp.append(mydata['ACTIVIDAD'][i])
        print("La ruta crítica del método es: " + "-".join(cp))

        #DURACION TOTAL DEL PROYECTO
        tdur = 0
        for i in range(ntask):
            if(mydata['MTi,j'][i] == 0):
                tdur = tdur + mydata ['Di,j'][i]
        print("La duración total del proyecto es de: " + str(tdur)+" Días")

        sys.exit()
    
    if prob_type == 0:
        print(r"""
        """)
        sys.exit()
        ###########
    print('\n------------------------------------------')
    global const_names
    const_num = int(input("CANTIDAD DE VARIABLES: >"))
    prod_nums = int(input("CANTIDAD DE RESTRICCIONES: >"))
    const_names = [x + str(i) for i in range(1, const_num + 1)]
    for i in range(1, prod_nums + 1):
        prod_val = i
        product_names.append(prod_val)
    print("-------------------------------------------")
    if prob_type == 1:
        for i in const_names:
            try:
                val = float(Fraction(input("INGRESE EL VALOR DE %s DE LA FUNCION OBJETIVO: >" % i)))
            except ValueError:
                print("POR FAVOR, INGRESE UN NUMERO")
                val = float(Fraction(input("INGRESE EL VALOR DE %s DE LA FUNCION OBJETIVO: >" % i)))
            z_equation.append(0 - int(val))
        z_equation.append(0)

        while len(z_equation) <= (const_num + prod_nums):
            z_equation.append(0)
        print("------------------------------------------")
        for prod in product_names:
            for const in const_names:
                try:
                    val = float(Fraction(input("INGRESE EL VALOR DE %s : >" % (const))))
                except ValueError:
                    print("EL VALOR DEBE SER UN NUMERO")
                    val = float(Fraction(input("INGRESE EL VALOR DE %s: >" % (const))))
                col_values.append(val)
            equate_prod = float(Fraction(input('MENOR IGUAL QUE %s: >' % prod)))
            col_values.append(equate_prod)

        final_cols = stdz_rows(col_values)
        i = len(const_names) + 1
        while len(const_names) < len(final_cols[0]) - 1:
            const_names.append('X' + str(i))
            solutions.append('X' + str(i))
            i += 1
        solutions.append(' Z')
        const_names.append('Bi')
        final_cols.append(z_equation)
        final_rows = np.array(final_cols).T.tolist()
        print("------------------------------------------")
        decimals = int(input('NUMERO DE DECIMALES A MOSTRAR : '))
        print('\n------------------------------------------')
        maximization(final_cols, final_rows)


def maximization(final_cols, final_rows):
    row_app = []
    last_col = final_cols[-1]
    min_last_row = min(last_col)
    min_manager = 1
    print("TABLA 1")
    try:
        final_pd = pd.DataFrame(np.array(final_cols), columns=const_names, index=solutions)
        print(final_pd)
    except:
        print('  ', const_names)
        i = 0
        for cols in final_cols:
            print(solutions[i], cols)
            i += 1
    count = 2
    pivot_element = 2
    while min_last_row < 0 < pivot_element != 1 and min_manager == 1 and count < 6:
        print("------------------------------------------")
        last_col = final_cols[-1]
        last_row = final_rows[-1]
        min_last_row = min(last_col)
        index_of_min = last_col.index(min_last_row)
        pivot_row = final_rows[index_of_min]
        index_pivot_row = final_rows.index(pivot_row)
        row_div_val = []
        i = 0
        for _ in last_row[:-1]:
            try:
                val = float(last_row[i] / pivot_row[i])
                if val <= 0:
                    val = 10000000000
                else:
                    val = val
                row_div_val.append(val)
            except ZeroDivisionError:
                val = 10000000000
                row_div_val.append(val)
            i += 1
        min_div_val = min(row_div_val)
        index_min_div_val = row_div_val.index(min_div_val)
        pivot_element = pivot_row[index_min_div_val]
        pivot_col = final_cols[index_min_div_val]
        index_pivot_col = final_cols.index(pivot_col)
        row_app[:] = []
        for col in final_cols:
            if col is not pivot_col and col is not final_cols[-1]:
                form = col[index_of_min] / pivot_element
                final_val = np.array(pivot_col) * form
                new_col = (np.round((np.array(col) - final_val), decimals)).tolist()
                final_cols[final_cols.index(col)] = new_col

            elif col is pivot_col:
                new_col = (np.round((np.array(col) / pivot_element), decimals)).tolist()
                final_cols[final_cols.index(col)] = new_col
            else:
                form = abs(col[index_of_min]) / pivot_element
                final_val = np.array(pivot_col) * form
                new_col = (np.round((np.array(col) + final_val), decimals)).tolist()
                final_cols[final_cols.index(col)] = new_col
        final_rows[:] = []
        re_final_rows = np.array(final_cols).T.tolist()
        final_rows = final_rows + re_final_rows

        if min(row_div_val) != 10000000000:
            min_manager = 1
        else:
            min_manager = 0
        print('ELEMENTO PIVOTE: %s' % pivot_element)
        print('COLUMNA PIVOTE: ', pivot_row)
        print('FILA PIVOTE: ', pivot_col)
        print("\n------------------------------------------")
        solutions[index_pivot_col] = const_names[index_pivot_row]

        print("TABLA %d" % count)
        try:
            final_pd = pd.DataFrame(np.array(final_cols), columns=const_names, index=solutions)
            print(final_pd)
        except:
            print("TABLA %d" % count)
            print('  ', const_names)
            i = 0
            for cols in final_cols:
                print(solutions[i], cols)
                i += 1
        count += 1
        last_col = final_cols[-1]
        last_row = final_rows[-1]
        min_last_row = min(last_col)
        index_of_min = last_col.index(min_last_row)
        pivot_row = final_rows[index_of_min]
        row_div_val = []
        i = 0
        for _ in last_row[:-1]:
            try:
                val = float(last_row[i] / pivot_row[i])
                if val <= 0:
                    val = 10000000000
                else:
                    val = val
                row_div_val.append(val)
            except ZeroDivisionError:
                val = 10000000000
                row_div_val.append(val)
            i += 1
        min_div_val = min(row_div_val)
        index_min_div_val = row_div_val.index(min_div_val)
        pivot_element = pivot_row[index_min_div_val]
        if pivot_element < 0:
            print(no_solution)
    if not pandas_av:
        print("""
        Instale Panda para que sus tablas se vean mejor, lo puede hacer mediante
        el comando: pip install pandas 
        """)




def stdz_rows2(column_values):
    final_cols = [column_values[x:x + const_num + 1] for x in range(0, len(column_values), const_num + 1)]
    sum_z = (0 - np.array(final_cols).sum(axis=0)).tolist()
    for _list in sum_z:
        z2_equation.append(_list)

    for cols in final_cols:
        while len(cols) < (const_num + (2 * prod_nums) - 1):
            cols.insert(-1, 0)

    i = const_num
    for sub_col in final_cols:
        sub_col.insert(i, -1)
        z2_equation.insert(-1, 1)
        i += 1

    for sub_col in final_cols:
        sub_col.insert(i, 1)
        i += 1

    while len(z2_equation) < len(final_cols[0]):
        z2_equation.insert(-1, 0)

    return final_cols


def stdz_rows(column_values):
    final_cols = [column_values[x:x + const_num + 1] for x in range(0, len(column_values), const_num + 1)]
    for cols in final_cols:
        while len(cols) < (const_num + prod_nums):
            cols.insert(-1, 0)

    i = const_num
    for sub_col in final_cols:
        sub_col.insert(i, 1)
        i += 1

    return final_cols


if __name__ == "__main__":
    main()

# I use python list and arrays(numpy) in most of this program
# it became simple coz python has a strong power in list and array manipulation and solution