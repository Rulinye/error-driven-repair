# Logit-scale check of the two interaction contrasts C4 and C5 (Section 4.3).
#
# usage: Rscript analysis/logit_check.R > analysis/logit_check.txt
#
# For each model, a binomial generalized linear mixed model is fitted with lme4 to the six primary
# conditions: the number of correct samples of a change under a condition (out of 5) depends on the error
# level (E2, E3, E4), the documentation level (D0, D2) and their interaction, with a random intercept for
# each change and one for each combination of change and condition. With E2 and D0 as reference levels,
#   C4 on the logit scale = (D2 - D0 at E2) - (D2 - D0 at E3) = -(coefficient E3:D2)
#   C5 on the logit scale = (D2 - D0 at E4) - (D2 - D0 at E2) =  (coefficient E4:D2)
# The fit uses lme4's defaults (Laplace approximation). If the two scales point in different directions,
# the interaction is reported as dependent on the scale; if the model cannot be fitted, only the
# percentage-point results count (Section 4.3). Warnings of the fit are printed with each model.

suppressPackageStartupMessages(library(lme4))

models <- c("gpt-6-luna", "gemini-3.8-flash", "qwen2.5-coder-7b", "codellama-7b")
primary <- c("E2D0", "E3D0", "E4D0", "E2D2", "E3D2", "E4D2")
args <- commandArgs(trailingOnly = FALSE)
here <- dirname(normalizePath(sub("^--file=", "", args[grep("^--file=", args)])))
results <- file.path(here, "..", "runs", "results")

cat(sprintf("lme4 %s, %s\n\n", packageVersion("lme4"), R.version.string))
for (m in models) {
  s <- read.csv(file.path(results, m, "samples.csv"), stringsAsFactors = FALSE)
  s <- s[s$template == "main" & s$condition %in% primary, ]
  s$correct <- s$correct == "True"
  d <- aggregate(correct ~ case + condition, data = s, FUN = sum)
  n <- aggregate(correct ~ case + condition, data = s, FUN = length)
  stopifnot(all(n$correct == 5), nrow(d) == 90 * 6)
  d$E <- factor(substr(d$condition, 1, 2), levels = c("E2", "E3", "E4"))
  d$D <- factor(substr(d$condition, 3, 4), levels = c("D0", "D2"))
  d$change <- factor(d$case)
  d$cell <- factor(paste(d$case, d$condition))
  warn <- character(0)
  fit <- withCallingHandlers(
    tryCatch(glmer(cbind(correct, 5 - correct) ~ E * D + (1 | change) + (1 | cell),
                   data = d, family = binomial),
             error = function(e) e),
    warning = function(w) { warn <<- c(warn, conditionMessage(w)); invokeRestart("muffleWarning") })
  cat(m, "\n")
  if (inherits(fit, "error")) {
    cat("  not fitted:", conditionMessage(fit), "\n\n")
    next
  }
  co <- summary(fit)$coefficients
  c4 <- -co["EE3:DD2", ]
  c5 <- co["EE4:DD2", ]
  cat(sprintf("  C4 (logit)  %+7.3f  SE %.3f  z %+6.2f\n", c4[1], co["EE3:DD2", 2], c4[1] / co["EE3:DD2", 2]))
  cat(sprintf("  C5 (logit)  %+7.3f  SE %.3f  z %+6.2f\n", c5[1], co["EE4:DD2", 2], c5[1] / co["EE4:DD2", 2]))
  vc <- as.data.frame(VarCorr(fit))
  cat(sprintf("  random-intercept SD: change %.3f, change x condition %.3f\n",
              vc$sdcor[vc$grp == "change"], vc$sdcor[vc$grp == "cell"]))
  cat("  singular fit:", isSingular(fit), "\n")
  msgs <- unique(c(warn, fit@optinfo$conv$lme4$messages))
  cat("  warnings:", if (length(msgs)) paste(msgs, collapse = " | ") else "none", "\n\n")
}
