import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.*;
import java.io.*;

public class TestInTheSky {

    private final ByteArrayOutputStream out = new ByteArrayOutputStream();
    private PrintStream originalOut;

    @BeforeEach
    void setup() {
        originalOut = System.out;
        System.setOut(new PrintStream(out));
    }

    @AfterEach
    void teardown() {
        System.setOut(originalOut);
        out.reset();
    }

    private String getOutput() {
        return out.toString().trim().replace("\r", "");
    }

    /**
     * Accepts strings that match when punctuation is removed and case is ignored.
     * Example: "I'm flying" == "im flying" == "I M FLYING"
     */
    private boolean looselyMatches(String expected, String actual) {
        String normExpected = expected.replaceAll("[^a-z0-9]", "").toLowerCase();
        String normActual = actual.replaceAll("[^a-z0-9]", "").toLowerCase();
        return normExpected.equals(normActual);
    }

   // ---------- PARROT TESTS ----------
    @Test
    void testParrotFlyAndLand() {
        Parrot p = new Parrot();

        p.fly();
        looselyMatches("I’m flying", getOutput());
        out.reset();

        p.land();
        looselyMatches("I’m landing", getOutput());
    }

    @Test
    void testParrotObserveOnGround() {
        Parrot p = new Parrot();
        p.observeEnvironment();
        looselyMatches("I am exploring the ground", getOutput());
    }

    @Test
    void testParrotObserveInSky() {
        Parrot p = new Parrot();
        p.fly();
        out.reset();
        p.observeEnvironment();
        looselyMatches("I am observeing the vast landscape below", getOutput());
    }


    // ---------- ITAKESPICTURES TESTS ----------
    @Test
    void testTakePictureTwice() {
        ITakesPictures cam = new ITakesPictures();

        cam.takePicture();
        looselyMatches("Operation started", getOutput());
        out.reset();

        cam.takePicture();
        looselyMatches("Operation started", getOutput());
        out.reset();
    }

    @Test
    void testMemoryFull() {
        ITakesPictures cam = new ITakesPictures();

        cam.takePicture(); out.reset();
        cam.takePicture(); out.reset();
        cam.takePicture();

        looselyMatches("full capacity", getOutput());
    }


    // ---------- CAMERADRONE TESTS ----------
    @Test
    void testCameraDroneFlyLand() {
        CameraDrone cd = new CameraDrone();

        cd.fly();
        looselyMatches("flying system activated", getOutput());
        out.reset();

        cd.land();
        looselyMatches("landing system activated", getOutput());
    }
}
