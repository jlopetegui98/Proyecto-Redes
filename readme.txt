Integrantes:
Ana Paula Argüelles Terrón C-312
Javier Alejandro Lopetegui C-312

En esta entrega del proyecto se agregan las funcionalidades necesarias para la detección de errores. Se implementaron dos métodos: el método de chequeo por suma('sum') y el método de redundancia cíclica('crc').

Es configurable desde el archivo 'conf.txt' del directorio 'data', el método que se usará, a través de la variable 'error_detection'. Para el caso del primer método la variable toma valor 'sum' y 'crc' para el segundo. Además se puede configurar el valor del generador(G) usado para el método 'crc' y el parámetro r, que será el número de bits del campo de chequeo.

En ambos casos el campo de chequeo('check') que se agrega al frame se crea en la función 'create_check_bits'. En caso de que error_detection = 'sum' este campo que se agrega será la representación en binario de la suma de los bytes del campo data del frame, de forma que el tamaño de este campo, que se especificará en el campo 'size_check' del frame, será igual al número de bytes necesarios para representar la suma obtenida. En el caso de que error_detection = 'crc' el campo  'check' será la representación en binario de R, cuyo valor será el resto de la división de data por 2^r entre el generador((data*2^r)%G), de forma que luego si se resta a data por 2^r el valor de R y se divide por G el resto tiene que ser 0. Luego, para el segundo método, el valor del campo 'size_check' del frame será el número de bytes que se requieren para representar el valor de R.

Luego de que una computadora recibe un frame chequea si el dato recibido no ha sufrido errores, usando la función 'check_data'. En esta función lo que se hace es, en caso de que error_detection = 'sum', verificar si los bits recibidos en el campo 'check' coinciden con la suma de los bytes de el dato recibido. Igualmente, en el caso de que error_detection = 'crc' se verifica si el resto de la división de data(recibida) por 2^r más el valor recibido en el campo ´check´, entre G es 0((data*2^r+R)%G = 0). Para los dos métodos, si el resultado no es el esperado, el flag ´received_frame' de la clase Host, toma valor 2.
