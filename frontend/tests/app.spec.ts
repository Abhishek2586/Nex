import { test, expect } from '@playwright/test';

test.describe('NEXORA Dashboard Flows', () => {
  // We should start with a clean state or at least known pages
  
  test('1. User Mode Navigation & History', async ({ page }) => {
    await page.goto('/');
    await page.getByText('Research Mode').click(); // toggle to User Mode
    
    // Ensure Research pages are hidden
    await expect(page.getByText('AI insights')).toBeHidden();
    
    // Check available pages
    await expect(page.getByRole('link', { name: 'Home' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Guidance' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'History' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'About' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Settings' })).toBeVisible();
    
    // Check History page loads
    await page.getByRole('link', { name: 'History' }).click();
    await expect(page.getByText('Your sessions are retained only in local storage.')).toBeVisible();
  });

  test('2. Research Mode: Normal Scenario', async ({ page }) => {
    test.setTimeout(60000);
    page.on('pageerror', err => console.log('Page Error:', err));
    await page.goto('/'); // Default is Research Mode if local storage is clear, but let's be sure
    // Ensure Research Mode (if not already)
    const toggle = page.getByLabel('Research Mode');
    if (!(await toggle.isChecked())) {
        await toggle.check();
    }
    
    await page.getByRole('link', { name: 'Overview' }).click();
    await page.getByRole('combobox', { name: 'Scenario' }).selectOption('normal');
    await page.getByRole('button', { name: 'Start synthetic session' }).click();

    // Verify session running
    await expect(page.locator('.status')).toHaveText('Status: running', { timeout: 15000 });
    await page.getByRole('link', { name: 'Live session' }).click();
    await expect(page).toHaveURL(/.*Live%20session/);
    await expect(page.getByRole('heading', { name: 'Model State & Current Interpretation' })).toBeVisible();
    
    // Stop session
    await page.getByRole('link', { name: 'Overview' }).click();
    await expect(page.getByText(/Status:\s*(running|stopped)/i)).toBeVisible({ timeout: 15000 });
    
    const stopBtn = page.getByRole('button', { name: 'Stop' });
    if (await stopBtn.isEnabled()) {
        await stopBtn.click();
    }
    await expect(stopBtn).toBeDisabled({ timeout: 10000 });
  });

  test('3. Research Mode: Missing Data Scenario', async ({ page }) => {
    test.setTimeout(60000);
    await page.goto('/Overview');
    
    await page.getByRole('combobox', { name: 'Scenario' }).selectOption('missing_data');
    await page.getByRole('button', { name: 'Start synthetic session' }).click();
    await expect(page.locator('.status')).toHaveText('Status: running', { timeout: 15000 });
    
    // Verify missing data abstention
    await page.getByRole('link', { name: 'Live session' }).click();
    await expect(page).toHaveURL(/.*Live%20session/);
    await expect(page.locator('[data-testid="recent-predictions"]')).toContainText(/Abstained.*(insufficient_coverage|unrepairable_gap|missing|low quality)/i, { timeout: 40000 });
    
    // Stop session
    await page.getByRole('link', { name: 'Overview' }).click();
    const stopBtn = page.getByRole('button', { name: 'Stop' });
    if (await stopBtn.isEnabled()) await stopBtn.click();
  });

  test('3.5 Research Mode: High Motion Scenario', async ({ page }) => {
    test.setTimeout(60000);
    await page.goto('/Overview');
    await page.getByRole('combobox', { name: 'Scenario' }).selectOption('high_motion');
    await page.getByRole('button', { name: 'Start synthetic session' }).click();
    await expect(page.locator('.status')).toHaveText('Status: running', { timeout: 15000 });
    
    await page.getByRole('link', { name: 'Live session' }).click();
    await expect(page).toHaveURL(/.*Live%20session/);
    await expect(page.locator('[data-testid="recent-predictions"]')).toContainText(/Abstained.*(?:high motion)/i, { timeout: 40000 });
    
    await page.getByRole('link', { name: 'Overview' }).click();
    const stopBtn = page.getByRole('button', { name: 'Stop' });
    if (await stopBtn.isEnabled()) await stopBtn.click();
  });

  test('4. Research Mode: Interventions & Prompt Isolation', async ({ page }) => {
    test.setTimeout(60000);
    await page.goto('/Overview');
    
    // Sustained posture triggers intervention
    await page.getByRole('combobox', { name: 'Scenario' }).selectOption('sustained_posture');
    await page.getByRole('button', { name: 'Start synthetic session' }).click();
    await expect(page.locator('.status')).toHaveText('Status: running', { timeout: 15000 });
    
    await page.getByRole('link', { name: 'Interventions' }).click();
    await expect(page.getByText('Prompts & feedback')).toBeVisible();
    
    const acceptBtn = page.getByRole('button', { name: 'accept' }).first();
    await expect(acceptBtn).toBeVisible({ timeout: 40000 });
    await acceptBtn.click();
    
    const completeBtn = page.getByRole('button', { name: 'complete' }).first();
    await expect(completeBtn).toBeVisible({ timeout: 10000 });
    await completeBtn.click();
    
    // Check prompt isolation
    await page.getByRole('link', { name: 'Overview' }).click();
    const stopBtn = page.getByRole('button', { name: 'Stop' });
    if (await stopBtn.isEnabled()) await stopBtn.click();
    
    await page.getByRole('combobox', { name: 'Scenario' }).selectOption('normal');
    await page.getByRole('button', { name: 'Start synthetic session' }).click();
    await expect(page.locator('.status')).toHaveText('Status: running', { timeout: 15000 });
    
    // Check user guidance page
    await page.getByText('Research Mode').click(); // switch to user
    await page.getByRole('link', { name: 'Guidance' }).click();
    await expect(page.getByText('No action is needed right now. Continue your work comfortably.')).toBeVisible();
    
    await page.getByRole('link', { name: 'Home' }).click();
    await page.getByRole('button', { name: 'End session' }).click();
  });

  test('5. AI Insights & Explanations', async ({ page }) => {
    test.setTimeout(90000);
    await page.goto('/Overview');
    await page.getByRole('combobox', { name: 'Scenario' }).selectOption('normal');
    await page.getByRole('button', { name: 'Start synthetic session' }).click();
    await expect(page.locator('.status')).toHaveText('Status: running', { timeout: 15000 });
    
    await page.getByRole('link', { name: 'AI insights' }).click();
    const explainBtn = page.getByRole('button', { name: 'Explain latest prediction' });
    await expect(explainBtn).toBeVisible({ timeout: 40000 });
    await explainBtn.click();
    
    await expect(page.getByText('Completeness delta:')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('.recharts-bar-rectangle')).toHaveCount(12, { timeout: 10000 });
  });

  test('6. Federated Lab & Rollback', async ({ page }) => {
    test.setTimeout(120000);
    
    // Check initial hash
    await page.goto('/Settings');
    const oldHashText = await page.getByText(/Active model hash:\s*([a-f0-9]+|None)/).innerText();
    const oldHash = oldHashText.match(/Active model hash:\s*([a-f0-9]+|None)/)?.[1] || '';

    await page.goto('/Federated%20%26%20privacy%20lab');
    await expect(page.getByText('Coordinator available').first()).toBeVisible({ timeout: 15000 });
    await expect(page.getByText('client-a').first()).toBeVisible();
    await expect(page.getByText('client-b').first()).toBeVisible();
    await expect(page.getByText('client-c').first()).toBeVisible();
    
    const runBtn = page.getByRole('button', { name: 'Run 1-round FedAvg' });
    await expect(runBtn).toBeEnabled({ timeout: 10000 });
    await runBtn.click();
    
    await expect(page.getByText(/1 round · (queued|training)/i).first()).toBeVisible({ timeout: 15000 });
    await expect(page.getByText(/1 round · completed/i).first()).toBeVisible({ timeout: 90000 });
    
    const activateBtn = page.getByRole('button', { name: 'Activate Candidate' }).first();
    await expect(activateBtn).toBeVisible();
    await activateBtn.click();
    
    await page.goto('/Settings');
    await expect(page.getByText(new RegExp(`Active model hash:\\s*(?!${oldHash})[a-f0-9]+`))).toBeVisible({ timeout: 10000 });
    
    await page.goto('/Federated%20%26%20privacy%20lab');
    const rollbackBtn = page.getByRole('button', { name: 'Rollback to Previous' }).first();
    await expect(rollbackBtn).toBeVisible();
    await rollbackBtn.click();
    
    await page.goto('/Settings');
    await expect(page.getByText(new RegExp(`Active model hash:\\s*${oldHash}`))).toBeVisible({ timeout: 10000 });
  });

  test('8. Accessibility: Reduce Motion Toggle', async ({ page }) => {
    await page.goto('/Settings');
    
    const toggle = page.getByRole('checkbox', { name: 'Reduce animations' });
    await toggle.check();
    
    // Check if body gets the class
    const body = page.locator('body');
    await expect(body).toHaveClass(/reduce-motion/);
    
    await toggle.uncheck();
    await expect(body).not.toHaveClass(/reduce-motion/);
  });

  test('9. Evidence Export', async ({ page }) => {
    await page.goto('/Evidence');
    await expect(page.getByText('Evidence package')).toBeVisible();
    
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Download ZIP Evidence' }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/^nexora-evidence-.*\.zip$/);
  });
});
