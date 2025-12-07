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

    @Test
    void testParrotFlyAndLand() {
        try {
            Parrot p = new Parrot();

            p.fly();
            assertTrue(looselyMatches("I'm flying", getOutput()));
            out.reset();

            p.land();
            assertTrue(looselyMatches("I'm landing", getOutput()));

        } catch (Exception e) {
            fail("Test failed with exception: " + e.getMessage());
        }
    }
}
