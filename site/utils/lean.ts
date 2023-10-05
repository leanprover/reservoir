import type {LanguageFn} from 'highlight.js'

// original from https://github.com/leanprover-community/highlightjs-leans, BSD 3, (c) 2020 Patrick Massot
// adapted to Lean 4 by https://github.com/leanprover/fp-lean, CC BY 4.0, (c) 2022 Microsoft Corporation
// with additional add-ons here
export const lean: LanguageFn = function(hljs) {
  const LEAN_KEYWORDS = {
    $pattern: /#?\w+/,
    keyword:
      'theorem|10 def abbrev class structure instance set_option ' +
      'example inductive coinductive ' +
      'axiom constant ' +
      'partial unsafe private protected ' +
      'if then else ' +
      'universe variable ' +
      'import open export prelude renaming hiding ' +
      'calc match nomatch with do by let have extends ' +
      'for in unless try catch finally mutual mut return continue break where rec while ' +
      'syntax macro_rules macro deriving ' +
      'termination_by ' +
      'fun ' +
      '#check #check_failure #eval #reduce #print ' +
      'section namespace end infix infixl infixr postfix prefix notation ' +
      'show from ' +
      'package lean_lib lean_exe require git ',
    built_in:
      'Type Prop|10 Sort rewrite rwa erw subst substs ' +
      'finish using ' +
      'unfold1 dunfold unfold_projs unfold_coes ' +
      'delta cc ac_rfl ' +
      'existsi|10 rcases intros introv by_cases ' +
      'rfl focus propext ' +
      'refine apply eapply fapply apply_with apply_instance ' +
      'rename revert generalize specialize clear ' +
      'contradiction by_contradiction by_contra trivial exfalso ' +
      'symmetry transitivity destruct econstructor ' +
      'injection injections ' +
      'swap solve1 abstract all_goals any_goals done ' +
      'fail_if_success success_if_fail guard_target guard_hyp ' +
      'replace at suffices ' +
      'congr congr_n congr_arg norm_num ring ',
    literal:
      '',
    meta:
      'noncomputable|10 private protected mutual',
    tag:
      'sorry admit',
  };

  const LEAN_IDENT_RE = /[A-Za-z_][\\w\u207F-\u209C\u1D62-\u1D6A\u2079\'0-9?]*/;

  const DASH_COMMENT = hljs.COMMENT('--', '$');
  const MULTI_LINE_COMMENT = hljs.COMMENT('/-[^-]', '-/');
  const DOC_COMMENT = {
    className: 'doctag',
    begin: '/-[-!]',
    end: '-/'
  };

  const ATTRIBUTE_DECORATOR = {
    className: 'meta',
    begin: '@\\[',
    end: '\\]'
  };

  const ATTRIBUTE_LINE = {
    className: 'meta',
    begin: '^attribute',
    end: '$'
  };

  const LEAN_DEFINITION =	{
    className: 'theorem',
    begin: '\\b(def|theorem|lemma|class|structure|(?<!deriving\\s+)instance)\\b',
    end: ':= | where',
    excludeEnd: true,
    contains: [
      {
        className: 'keyword',
        begin: /extends/
      },
      hljs.inherit(hljs.TITLE_MODE, {
        begin: LEAN_IDENT_RE
      }),
      {
        className: 'params',
        begin: /[([{]/, end: /[)\]}]/, endsParent: false,
        keywords: LEAN_KEYWORDS,
      },
      {
        className: 'symbol',
        begin: /:/,
        endsParent: true
      },
    ],
    keywords: LEAN_KEYWORDS
  }
  return {
    name: "lean",
    keywords: LEAN_KEYWORDS,
    contains: [
      hljs.QUOTE_STRING_MODE,
      hljs.NUMBER_MODE,
      DASH_COMMENT,
      MULTI_LINE_COMMENT,
      DOC_COMMENT,
      LEAN_DEFINITION,
      ATTRIBUTE_DECORATOR,
      ATTRIBUTE_LINE,
      { begin: /⟨/ } // relevance booster
    ]
  }
}

export default lean
