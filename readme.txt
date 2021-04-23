Integrantes:
Ana Paula Arg�elles Terr�n C-312
Javier Alejandro Lopetegui C-312

En esta entrega del proyecto se agregan las funcionalidades necesarias para la detecci�n de errores. Se implementaron dos m�todos: el m�todo de chequeo por suma('sum') y el m�todo de redundancia c�clica('crc').

Es configurable desde el archivo 'conf.txt' del directorio 'data', el m�todo que se usar�, a trav�s de la variable 'error_detection'. Para el caso del primer m�todo la variable toma valor 'sum' y 'crc' para el segundo. Adem�s se puede configurar el valor del generador(G) usado para el m�todo 'crc' y el par�metro r, que ser� el n�mero de bits del campo de chequeo.

En ambos casos el campo de chequeo('check') que se agrega al frame se crea en la funci�n 'create_check_bits'. En caso de que error_detection = 'sum' este campo que se agrega ser� la representaci�n en binario de la suma de los bytes del campo data del frame, de forma que el tama�o de este campo, que se especificar� en el campo 'size_check' del frame, ser� igual al n�mero de bytes necesarios para representar la suma obtenida. En el caso de que error_detection = 'crc' el campo  'check' ser� la representaci�n en binario de R, cuyo valor ser� el resto de la divisi�n de data por 2^r entre el generador((data*2^r)%G), de forma que luego si se resta a data por 2^r el valor de R y se divide por G el resto tiene que ser 0. Luego, para el segundo m�todo, el valor del campo 'size_check' del frame ser� el n�mero de bytes que se requieren para representar el valor de R.

Luego de que una computadora recibe un frame chequea si el dato recibido no ha sufrido errores, usando la funci�n 'check_data'. En esta funci�n lo que se hace es, en caso de que error_detection = 'sum', verificar si los bits recibidos en el campo 'check' coinciden con la suma de los bytes de el dato recibido. Igualmente, en el caso de que error_detection = 'crc' se verifica si el resto de la divisi�n de data(recibida) por 2^r m�s el valor recibido en el campo �check�, entre G es 0((data*2^r+R)%G = 0). Para los dos m�todos, si el resultado no es el esperado, el flag �received_frame' de la clase Host, toma valor 2.
