# Tasks

## Core issues

 * non-primitive types don't work with Simulate
   * problem is output validation
   * should at least give warnings
   * when errors are caught by evaluator's, should _record relevant
     information from the stack trace
   * move expt.py into core

## CLI improvements
 
  * results.py validate [--require xxx] [--purge] ...
  * results.py delete-obsolete 

## Caching

 * Check if disabling caching from the command-line works
 * Revisit how llm_util does caching - as is using the cache bypasses echos

## Experimentation

 * Run experiments in sports_understanding
     * use smaller models till the task gets "interesting"?

## Code quality/etc

 * More guidance for claude/devs on defense programming
 * Standardize implement strategies: [un]structured_baseline, pot, workflow, react
