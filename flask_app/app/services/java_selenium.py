import os
import subprocess
import tempfile
import json
from typing import Dict, Any

class JavaSeleniumRunner:
    """Service to execute Java Selenium code"""
    
    def __init__(self):
        self.java_template = """
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import java.time.Duration;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.HashMap;
import java.util.Map;

public class SeleniumTest {
    public static void main(String[] args) {
        WebDriver driver = null;
        Map<String, Object> result = new HashMap<>();
        
        try {
            ChromeOptions options = new ChromeOptions();
            options.addArguments("--headless");
            options.addArguments("--no-sandbox");
            options.addArguments("--disable-dev-shm-usage");
            
            driver = new ChromeDriver(options);
            WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
            
            // User code will be injected here
            {user_code}
            
            result.put("success", true);
            result.put("message", "Selenium test executed successfully");
            
        } catch (Exception e) {
            result.put("success", false);
            result.put("error", e.getMessage());
        } finally {
            if (driver != null) {
                driver.quit();
            }
        }
        
        try {
            ObjectMapper mapper = new ObjectMapper();
            System.out.println(mapper.writeValueAsString(result));
        } catch (Exception e) {
            System.out.println("{\\"success\\": false, \\"error\\": \\"" + e.getMessage() + "\\"}");
        }
    }
}
"""

    def execute_java_selenium(self, java_code: str, dependencies: list = None) -> Dict[str, Any]:
        """Execute Java Selenium code and return results"""
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write Java file
                java_file = os.path.join(temp_dir, "SeleniumTest.java")
                full_code = self.java_template.replace("{user_code}", java_code)
                
                with open(java_file, 'w') as f:
                    f.write(full_code)
                
                # Create basic pom.xml for Maven dependencies
                pom_content = self._create_maven_pom(dependencies or [])
                pom_file = os.path.join(temp_dir, "pom.xml")
                with open(pom_file, 'w') as f:
                    f.write(pom_content)
                
                # Compile and run
                compile_result = subprocess.run(
                    ['javac', '-cp', self._get_classpath(), java_file],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir
                )
                
                if compile_result.returncode != 0:
                    return {
                        'success': False,
                        'error': f'Compilation failed: {compile_result.stderr}'
                    }
                
                # Run the compiled Java code
                run_result = subprocess.run(
                    ['java', '-cp', f'{self._get_classpath()}:{temp_dir}', 'SeleniumTest'],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    timeout=30
                )
                
                if run_result.returncode != 0:
                    return {
                        'success': False,
                        'error': f'Execution failed: {run_result.stderr}'
                    }
                
                # Parse result
                try:
                    return json.loads(run_result.stdout.strip())
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': 'Failed to parse execution result',
                        'output': run_result.stdout
                    }
                    
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Execution timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_classpath(self) -> str:
        """Get the classpath for Selenium dependencies"""
        # This should point to your Selenium JAR files
        # In production, you'd want to manage this with Maven or Gradle
        selenium_path = "/opt/selenium"  # Update this path
        if os.path.exists(selenium_path):
            return f"{selenium_path}/*"
        return "."

    def _create_maven_pom(self, dependencies: list) -> str:
        """Create a basic Maven POM file"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.automation</groupId>
    <artifactId>selenium-test</artifactId>
    <version>1.0.0</version>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <selenium.version>4.15.0</selenium.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.seleniumhq.selenium</groupId>
            <artifactId>selenium-java</artifactId>
            <version>${{selenium.version}}</version>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>2.15.2</version>
        </dependency>
        <!-- Additional dependencies -->
        {self._format_dependencies(dependencies)}
    </dependencies>
</project>"""

    def _format_dependencies(self, dependencies: list) -> str:
        """Format additional Maven dependencies"""
        if not dependencies:
            return ""
        
        dep_xml = ""
        for dep in dependencies:
            if isinstance(dep, dict):
                group_id = dep.get('groupId', '')
                artifact_id = dep.get('artifactId', '')
                version = dep.get('version', '')
                if group_id and artifact_id and version:
                    dep_xml += f"""
        <dependency>
            <groupId>{group_id}</groupId>
            <artifactId>{artifact_id}</artifactId>
            <version>{version}</version>
        </dependency>"""
        return dep_xml

def run_java_selenium_demo():
    """Demo function for Java Selenium execution"""
    runner = JavaSeleniumRunner()
    sample_code = """
            // Navigate to example.com
            driver.get("https://example.com");
            
            // Get page title
            String title = driver.getTitle();
            result.put("title", title);
            result.put("url", driver.getCurrentUrl());
            
            // Find and interact with elements
            WebElement heading = driver.findElement(By.tagName("h1"));
            result.put("heading", heading.getText());
    """
    
    return runner.execute_java_selenium(sample_code)