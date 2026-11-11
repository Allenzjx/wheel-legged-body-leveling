import fs from 'node:fs';

export function renderMethod50({e,table,equation}) {
  const m=JSON.parse(fs.readFileSync('content/method50.json','utf8'));
  const observations=m.observations.map(o=>`<div><h4>${e(o.name)}</h4><p>${e(o.description)}</p></div>`).join('');
  const stages=m.stages.map((s,i)=>`<li><span class="stage-number">${i+1}</span><div class="stage-body"><h4>${e(s.name)}</h4><p>${e(s.objective)}</p><details class="stage-details"><summary>Training procedure</summary><p>${e(s.execution)}</p><p>${e(s.handoff)}</p></details></div></li>`).join('');
  return `<section class="section" id="residual">
    <h2><span class="section-number">3</span> ${e(m.title)}</h2>
    <p class="section-intro">${e(m.overview)}</p>
    <figure><div class="control-diagram" role="img" aria-label="Recorded reference and measured robot state feed residual PPO; bounded joint and wheel corrections form the robot commands">
      <div><h4>Reference and state</h4><p>Recorded joint and wheel targets<br>Body, contact and traversal state</p></div><span class="arrow" aria-hidden="true">→</span>
      <div class="learned"><h4>Residual PPO</h4><p>State-dependent corrections<br>15 Hz policy decisions</p></div><span class="arrow" aria-hidden="true">→</span>
      <div><h4>Robot commands</h4><p>8 joint-angle + 4 wheel-speed targets<br>120 Hz physical interface</p></div>
    </div><figcaption>Recorded motion establishes the crossing reference. The learned residual adapts the joint and wheel commands as the support configuration changes.</figcaption></figure>
    ${equation(1,'u<sub>t</sub> = C(u<sub>t</sub><sup>nom</sup> + Δu<sub>t</sub>, o<sub>t</sub>)','u<sup>nom</sup> denotes the reference command, Δu the learned residual and o the measured state. C applies contact coordination, joint-range, command-rate and actuator limits.')}

    <h3>3.1 State representation</h3><div class="observation-grid method-observations">${observations}</div>
    <h3>3.2 Policy and action representation</h3>
    <p>The full controller requests corrections to eight leg-joint angles and four wheel speeds. Gaussian sampling provides exploration during training. Each request is scaled and bounded according to the active motion phase before the final actuator mapping.</p>
    ${equation(2,'r<sub>i</sub> = C<sub>phase,i</sub> tanh(z<sub>i</sub>)','z is the Gaussian policy request. C<sub>phase,i</sub> specifies a physical correction scale in degrees for joints or radians per second for wheels. The bounded residual is a requested correction; subsequent constraints determine the applied target.')}
    <details class="technical"><summary>Actor architecture</summary>${table('Learned components of the 50 mm controller',['Component','Architecture','Policy output'],m.architecture.map(r=>r.map(e)))}<p>${e(m.architectureNote)}</p></details>

    <h3 id="training50">3.3 Training across the crossing sequence</h3>
    <p>All four stages concern the same 50 mm obstacle height. The progression introduces later support-transfer tasks while preserving the behavior learned in preceding stages.</p>
    <ol class="timeline">${stages}</ol>

    <h3>3.4 PPO optimization</h3>
    <p>Simulator rollouts collect observations, sampled residual requests and rewards. The critic estimates return, and generalized advantage estimation (GAE) combines rewards and value estimates into the actor's training signal. PPO updates the eligible actor component through a clipped likelihood-ratio objective.</p>
    ${equation(3,'L<sup>CLIP</sup>(θ) = E[min(ρ<sub>t</sub> Â<sub>t</sub>, clip(ρ<sub>t</sub>, 1 − ε, 1 + ε) Â<sub>t</sub>)]','ρ is the new-to-old action probability ratio, Â is the estimated advantage and ε = 0.2. Probability-ratio clipping controls the policy update; the physical residual bounds separately constrain the command.')}
    <details class="technical"><summary>Optimization settings by stage</summary>${table('50 mm training settings',['Setting','Early motion','Local refinements'],m.optimization.map(r=>r.map(e)))}<p>${e(m.optimizationNote)}</p></details>
    <div class="two-col"><div><h3>Reward design</h3><p>${e(m.reward)}</p></div><div><h3>Evaluation protocol</h3><p>${e(m.evaluation)}</p></div></div>
  </section>`;
}
