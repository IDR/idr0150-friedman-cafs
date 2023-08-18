package ij.io;
import ij.gui.*;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class ExtractPoints {

    /// Extracts the points from ImageJ Polygon ROIs and saves them as csv

    public static void main(String args[]) throws IOException {
        String path = "/tmp/idr0150/2-METABRIC";   // Directory with the *.roi files
        File csvPath = new File(path+"/csv");
        if (!csvPath.exists()) // create a subdirectory csv for the exported files
            csvPath.mkdir();

        for (File roiFile : (new File(path).listFiles())) {
            if (roiFile.isDirectory())
                continue;
            RoiDecoder dec = new RoiDecoder(roiFile.getAbsolutePath());
            Roi roi = dec.getRoi();
            if (roi instanceof PolygonRoi) {
                PolygonRoi p = (PolygonRoi) roi;
                System.out.println(p);
                FileWriter outFile = new FileWriter(path+"/csv/"+roiFile.getName()+".csv");
                try (BufferedWriter out = new BufferedWriter(outFile)) {
                    out.write("x,y\n");
                    for (int i=0; i<p.size(); i++) {
                        int x = p.getXCoordinates()[i]+(int)p.getXBase();
                        int y = p.getYCoordinates()[i]+(int)p.getYBase();
                        out.write(x+","+y+"\n");
                    }
                }
            }
        }
    }
}

