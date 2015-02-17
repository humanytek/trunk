/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package serial;

import javax.swing.JApplet;
import jssc.SerialPort;
import jssc.SerialPortException;

/**
 *
 * @author prajul
 */
public class serial_comm extends Applet {

    /**
     * Initialization method that will be called after the applet is loaded into
     * the browser.
     */
    public void init() {
//        SerialPort serialPort = new SerialPort("/dev/ttyS0");
//        try {
//            serialPort.openPort();//Open serial port
//            serialPort.setParams(SerialPort.BAUDRATE_9600, 
//                                 SerialPort.DATABITS_8,
//                                 SerialPort.STOPBITS_1,
//                                 SerialPort.PARITY_NONE);//Set params. Also you can set params by this string: serialPort.setParams(9600, 8, 1, 0);
//            serialPort.writeBytes("This is a test string".getBytes());//Write data to port
//            serialPort.closePort();//Close serial port
//        }
//        catch (SerialPortException ex) {
//            System.out.println(ex);
//        }
        // TODO start asynchronous download of heavy resources
    }
    
    public void setMessage(String message) {
    	String[] ports = SerialPortList.getPortNames();
        if(ports.length > 0){
            portName = ports[0];
        }
        SerialPort serialPort = new SerialPort(portName);
        try {
            serialPort.openPort();//Open serial port
            serialPort.setParams(SerialPort.BAUDRATE_9600, 
                                 SerialPort.DATABITS_8,
                                 SerialPort.STOPBITS_1,
                                 SerialPort.PARITY_NONE);//Set params. Also you can set params by this string: serialPort.setParams(9600, 8, 1, 0);
            serialPort.writeBytes("This is a test string".getBytes());//Write data to port
            serialPort.closePort();//Close serial port
        }
        catch (SerialPortException ex) {
            System.out.println(ex);
        }
    }
    // TODO overwrite start(), stop() and destroy() methods
}
