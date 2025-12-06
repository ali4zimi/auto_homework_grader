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
        return out.toString().trim().replace("\r","");
    }


    @Test
    void testParrotFlyAndLand() {
        try {
            Parrot p = new Parrot();

            p.fly();
            assertEquals("I'm flying", getOutput());
            out.reset();

            p.land();
            assertEquals("I'm landing", getOutput());
        } catch (Exception e) {
            fail("Test failed with exception: " + e.getMessage());
        }
    }
}
