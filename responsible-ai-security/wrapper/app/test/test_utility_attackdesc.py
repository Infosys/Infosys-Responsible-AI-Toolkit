from src.service.utility import Utility


def test_attackDesc_returns_descriptions_for_known_attacks():
    keys = [
        "Poisoning",
        "MembershipInferenceRule",
        "MembershipInferenceBlackBox",
        "LabelOnlyDecisionBoundary",
        "AttributeInferenceWhiteBoxLifestyleDecisionTree",
        "AttributeInferenceWhiteBoxDecisionTree",
        "InferenceLabelOnlyGap",
        "AttributeInference",
        "CarliniL2Method",
        "Deepfool",
        "Boundary",
        "UniversalPerturbation",
        "FastGradientMethod",
        "SpatialTransformation",
        "Pixel",
        "Wasserstein",
        "Square",
        "ProjectGradientDescentImage",
        "BasicIterativeMethod",
        "SaliencyMapMethod",
        "IterativeFrameSaliency",
        "SimBA",
        "NewtonFool",
        "ElasticNet",
        "QueryEfficient",
        "ProjectedGradientDescentTabular",
        "DecisionTree",
        "HopSkipJumpTabular",
        "ZerothOrderOptimization",
        "HopSkipJumpImage",
        "QueryEfficientGradientAttackEndPoint",
        "BoundaryAttackEndPoint",
        "HopSkipJumpAttackEndPoint",
        "LabelOnlyGapAttackEndPoint",
        "MembershipInferenceBlackBoxRuleBasedAttackEndPoint",
        "LabelOnlyDecisionBoundaryAttackEndPoint",
        "MembershipInferenceBlackBoxAttackEndPoint",
        "VirtualAdversarialMethod",
        "GeometricDecisionBasedAttack",
        "Threshold",
        "Augly",
    ]

    for k in keys:
        s = Utility.attackDesc(k)
        assert isinstance(s, str)
        assert len(s) > 0


def test_attackDesc_unknown_returns_empty_string():
    assert Utility.attackDesc("UnknownAttackTypeXYZ") == ""
