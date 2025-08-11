# Fix Code Quality Issues

I'll automatically fix code quality issues in your project by running the formatter and then addressing any remaining issues that couldn't be automatically resolved.

## What I'll Do:

1. **Run Automatic Formatter**
   - Execute `./fix.sh` to run ruff (Python) and prettier (TypeScript) formatters
   - This fixes most code style issues automatically

2. **Run Type Checking**
   - Execute ty for fast Python type checking
   - Identify type annotation issues and inconsistencies

3. **Identify Remaining Issues**
   - Check for any remaining linting errors or warnings
   - Look for type issues that require manual intervention

4. **Fix Manual Issues**
   - Address any remaining code quality problems
   - Fix import sorting, unused imports, and other issues
   - Ensure proper docstring formatting
   - Fix any type annotations or other manual fixes needed

5. **Verify Results**
   - Run the formatters and type checker again to ensure all issues are resolved
   - Confirm code quality and type safety is improved

## Running the Fix Process:

First, let me run the automatic formatter:

```bash
./fix.sh
```

Then I'll check for any remaining issues and fix them manually.

---

*This command helps maintain consistent code quality across your Python and TypeScript files.*